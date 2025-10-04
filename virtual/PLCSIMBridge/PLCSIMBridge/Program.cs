using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;
using Siemens.Simatic.Simulation.Runtime;

namespace PLCSIMBridge
{
    class Program
    {
        private static IInstance plcInstance = null;
        private static TcpListener server = null;
        private static bool running = true;
        private static Dictionary<int, string> markerByteMapping = new Dictionary<int, string>();
        private static string instanceName = "GestureControl"; // Default
        private static int connectedClients = 0;

        static void Main(string[] args)
        {
            // Parse command-line arguments
            if (args.Length > 0)
            {
                instanceName = args[0];
            }

            Console.CancelKeyPress += OnCancelKeyPress;

            Console.WriteLine("╔════════════════════════════════════════════╗");
            Console.WriteLine("║  PLCSIM Advanced Bridge Server             ║");
            Console.WriteLine("╚════════════════════════════════════════════╝");
            Console.WriteLine($"Target instance: {instanceName}");
            Console.WriteLine($"Press Ctrl+C to shutdown gracefully\n");

            if (!ConnectToPLCSIM(instanceName))
            {
                Console.WriteLine("\n[ERROR] Failed to connect to PLCSIM");
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                return;
            }

            StartTCPServer(5000);
        }

        static void OnCancelKeyPress(object sender, ConsoleCancelEventArgs e)
        {
            e.Cancel = true; // Prevent immediate termination
            Console.WriteLine("\n\n[SHUTDOWN] Graceful shutdown initiated...");
            running = false;

            if (server != null)
            {
                server.Stop();
                Console.WriteLine("[SHUTDOWN] TCP server stopped");
            }

            if (plcInstance != null)
            {
                Console.WriteLine("[SHUTDOWN] Disconnecting from PLCSIM...");
                // API handles cleanup automatically
            }

            Console.WriteLine("[SHUTDOWN] Bridge shutdown complete");
            Environment.Exit(0);
        }

        static bool ConnectToPLCSIM(string instanceName)
        {
            try
            {
                Console.WriteLine($"[CONNECT] Searching for PLCSIM instances...");

                var instances = SimulationRuntimeManager.RegisteredInstanceInfo;

                if (instances.Length == 0)
                {
                    Console.WriteLine("[ERROR] No PLCSIM instances found!");
                    Console.WriteLine("        Make sure PLCSIM Advanced is running");
                    return false;
                }

                Console.WriteLine($"[FOUND] {instances.Length} instance(s):");

                int targetIndex = -1;
                for (int i = 0; i < instances.Length; i++)
                {
                    string status = instances[i].Name == instanceName ? " [TARGET]" : "";
                    Console.WriteLine($"        - {instances[i].Name} (ID: {instances[i].ID}){status}");
                    if (instances[i].Name == instanceName)
                    {
                        targetIndex = i;
                    }
                }

                if (targetIndex == -1)
                {
                    Console.WriteLine($"[WARNING] Instance '{instanceName}' not found");
                    Console.WriteLine($"[FALLBACK] Using first available: {instances[0].Name}");
                    targetIndex = 0;
                }

                Console.WriteLine($"[CONNECT] Connecting to: {instances[targetIndex].Name}...");
                plcInstance = SimulationRuntimeManager.CreateInterface(instances[targetIndex].ID);

                Console.WriteLine("[UPDATE] Loading tag list...");
                plcInstance.UpdateTagList();

                // Auto-discover Marker byte tags
                Console.WriteLine("\n[MAPPING] Auto-discovered Marker Byte tags:");
                var tagList = plcInstance.TagInfos;
                int byteIndex = 0;
                for (int i = 0; i < tagList.Length; i++)
                {
                    if (tagList[i].Area.ToString() == "Marker" && tagList[i].DataType.ToString() == "Byte")
                    {
                        markerByteMapping[byteIndex] = tagList[i].Name;
                        Console.WriteLine($"          %MB{byteIndex} → {tagList[i].Name}");
                        byteIndex++;
                    }
                }

                if (markerByteMapping.Count == 0)
                {
                    Console.WriteLine("[WARNING] No Marker Byte tags found!");
                    Console.WriteLine("          Create Byte tags in TIA Portal for I/O access");
                }

                Console.WriteLine($"\n[SUCCESS] Connected to: {instances[targetIndex].Name}");
                Console.WriteLine($"[STATUS]  Operating State: {plcInstance.OperatingState}");
                Console.WriteLine($"[STATUS]  Mapped bytes: {markerByteMapping.Count}");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] {ex.Message}");
                return false;
            }
        }

        static void StartTCPServer(int port)
        {
            try
            {
                server = new TcpListener(IPAddress.Any, port);
                server.Start();
                Console.WriteLine($"\n[SERVER] TCP Server listening on port {port}");
                Console.WriteLine($"[READY]  Waiting for Python connections...");
                Console.WriteLine("─────────────────────────────────────────────\n");

                while (running)
                {
                    if (server.Pending())
                    {
                        TcpClient client = server.AcceptTcpClient();
                        Thread clientThread = new Thread(() => HandleClient(client));
                        clientThread.Start();
                    }
                    Thread.Sleep(100);
                }
            }
            catch (SocketException ex)
            {
                Console.WriteLine($"[ERROR] Server error: {ex.Message}");
                if (ex.ErrorCode == 10048)
                {
                    Console.WriteLine($"[ERROR] Port {port} is already in use");
                    Console.WriteLine($"[ERROR] Another bridge instance may be running");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Unexpected error: {ex.Message}");
            }
        }

        static void HandleClient(TcpClient client)
        {
            connectedClients++;
            string clientId = $"Client#{connectedClients}";
            string remoteEndPoint = client.Client.RemoteEndPoint.ToString();

            Console.WriteLine($"[CONNECT] {clientId} connected from {remoteEndPoint}");
            UpdateStatusLine();

            NetworkStream stream = client.GetStream();
            byte[] buffer = new byte[1024];

            try
            {
                while (client.Connected && running)
                {
                    if (stream.DataAvailable)
                    {
                        int bytes = stream.Read(buffer, 0, buffer.Length);
                        string command = Encoding.ASCII.GetString(buffer, 0, bytes).Trim();

                        Console.WriteLine($"[RX] {clientId}: {command}");
                        string response = ProcessCommand(command);

                        byte[] responseBytes = Encoding.ASCII.GetBytes(response + "\n");
                        stream.Write(responseBytes, 0, responseBytes.Length);
                        Console.WriteLine($"[TX] {clientId}: {response}");
                    }
                    Thread.Sleep(10);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] {clientId} error: {ex.Message}");
            }
            finally
            {
                client.Close();
                connectedClients--;
                Console.WriteLine($"[DISCONNECT] {clientId} disconnected");
                UpdateStatusLine();
            }
        }

        static void UpdateStatusLine()
        {
            Console.WriteLine($"[STATUS] Active connections: {connectedClients}");
        }

        static string ProcessCommand(string command)
        {
            try
            {
                string[] parts = command.Split(' ');

                if (parts.Length < 4)
                    return "ERROR: Invalid command format (need: ACTION AREA BYTE BIT [VALUE])";

                string action = parts[0].ToUpper();
                string area = parts[1].ToUpper();
                int byteOffset = int.Parse(parts[2]);
                int bitOffset = int.Parse(parts[3]);

                if (action == "WRITE" && parts.Length >= 5)
                {
                    bool value = parts[4] == "1" || parts[4].ToUpper() == "TRUE";
                    return WriteBit(area, byteOffset, bitOffset, value);
                }
                else if (action == "READ")
                {
                    return ReadBit(area, byteOffset, bitOffset);
                }
                else
                {
                    return "ERROR: Unknown command (use READ or WRITE)";
                }
            }
            catch (FormatException)
            {
                return "ERROR: Invalid number format in command";
            }
            catch (Exception ex)
            {
                return $"ERROR: {ex.Message}";
            }
        }

        static string WriteBit(string area, int byteOffset, int bitOffset, bool value)
        {
            try
            {
                string tagName = GetTagNameForAddress(area, byteOffset);

                if (tagName == null)
                    return $"ERROR: No tag mapped for %{area}B{byteOffset}";

                if (bitOffset < 0 || bitOffset > 7)
                    return $"ERROR: Bit offset must be 0-7, got {bitOffset}";

                byte currentValue = plcInstance.ReadUInt8(tagName);

                byte newValue;
                if (value)
                    newValue = (byte)(currentValue | (1 << bitOffset));
                else
                    newValue = (byte)(currentValue & ~(1 << bitOffset));

                plcInstance.WriteUInt8(tagName, newValue);
                return "OK";
            }
            catch (Exception ex)
            {
                return $"ERROR: {ex.Message}";
            }
        }

        static string ReadBit(string area, int byteOffset, int bitOffset)
        {
            try
            {
                string tagName = GetTagNameForAddress(area, byteOffset);

                if (tagName == null)
                    return $"ERROR: No tag mapped for %{area}B{byteOffset}";

                if (bitOffset < 0 || bitOffset > 7)
                    return $"ERROR: Bit offset must be 0-7, got {bitOffset}";

                byte value = plcInstance.ReadUInt8(tagName);
                bool bitValue = (value & (1 << bitOffset)) != 0;
                return bitValue ? "1" : "0";
            }
            catch (Exception ex)
            {
                return $"ERROR: {ex.Message}";
            }
        }

        static string GetTagNameForAddress(string area, int byteOffset)
        {
            if (area == "M" && markerByteMapping.ContainsKey(byteOffset))
            {
                return markerByteMapping[byteOffset];
            }
            return null;
        }
    }
}