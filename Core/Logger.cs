using System;
using System.IO;
using SysDebug = System.Diagnostics.Debug;

namespace BAC_MCP.Core
{
    public static class Logger
    {
        private static readonly string LogDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "BAC_MCP", "logs");

        private static readonly object _lock = new();
        private static bool _initialized = false;

        public static void Initialize()
        {
            if (_initialized) return;

            try
            {
                Directory.CreateDirectory(LogDirectory);
                _initialized = true;
                Info("Logger initialized");
            }
            catch (Exception ex)
            {
                SysDebug.WriteLine($"[BAC_MCP] Failed to initialize logger: {ex.Message}");
            }
        }

        public static void Info(string message) => Log("INFO", message);

        public static void Debug(string message)
        {
#if DEBUG
            Log("DEBUG", message);
#endif
        }

        public static void Warning(string message) => Log("WARN", message);

        public static void Error(string message, Exception? ex = null)
        {
            string fullMessage = ex != null
                ? $"{message} | Exception: {ex.GetType().Name}: {ex.Message}"
                : message;

            Log("ERROR", fullMessage);

            if (ex != null)
            {
                Log("ERROR", $"StackTrace: {ex.StackTrace}");
            }
        }

        public static void McpRequest(string method, int requestId)
        {
            Log("MCP", $"[REQ {requestId}] {method}");
        }

        public static void McpResponse(int requestId, bool success, string? error = null)
        {
            if (success)
                Log("MCP", $"[RES {requestId}] Success");
            else
                Log("MCP", $"[RES {requestId}] Error: {error}");
        }

        private static void Log(string level, string message)
        {
            try
            {
                if (!_initialized)
                {
                    Initialize();
                }

                string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
                string entry = $"[{timestamp}] [{level,-5}] {message}";

                // Write to debug output
                SysDebug.WriteLine($"[BAC_MCP] {entry}");

                // Write to file
                string fileName = $"bac_mcp_{DateTime.Now:yyyy-MM-dd}.log";
                string filePath = Path.Combine(LogDirectory, fileName);

                lock (_lock)
                {
                    File.AppendAllText(filePath, entry + Environment.NewLine);
                }

                // Cleanup old logs (keep last 7 days)
                CleanupOldLogs();
            }
            catch
            {
                // Silent fail for logging - don't crash the app
            }
        }

        private static DateTime _lastCleanup = DateTime.MinValue;

        private static void CleanupOldLogs()
        {
            // Only check once per day
            if ((DateTime.Now - _lastCleanup).TotalHours < 24) return;
            _lastCleanup = DateTime.Now;

            try
            {
                var cutoff = DateTime.Now.AddDays(-7);
                var files = Directory.GetFiles(LogDirectory, "bac_mcp_*.log");

                foreach (var file in files)
                {
                    var fileInfo = new FileInfo(file);
                    if (fileInfo.LastWriteTime < cutoff)
                    {
                        fileInfo.Delete();
                    }
                }
            }
            catch
            {
                // Silent fail
            }
        }

        public static string GetLogDirectory() => LogDirectory;
    }
}
