using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace BAC_MCP.Mcp
{
    public class StdioTransport : IDisposable
    {
        private Process _process;
        private StreamWriter _input;
        private StreamReader _output;
        private CancellationTokenSource _cts;

        public event Action<string>? OnMessageReceived;
        public event Action<string>? OnErrorReceived;

        public StdioTransport(string command, string arguments, Dictionary<string, string>? environmentVariables = null)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = command,
                Arguments = arguments,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8
            };

            if (environmentVariables != null)
            {
                foreach (var kvp in environmentVariables)
                {
                    psi.EnvironmentVariables[kvp.Key] = kvp.Value;
                }
            }

            _process = new Process { StartInfo = psi };
            _process.ErrorDataReceived += (s, e) =>
            {
                if (e.Data != null)
                {
                    Debug.WriteLine($"[MCP Error] {e.Data}");
                    OnErrorReceived?.Invoke(e.Data);
                }
            };
        }

        public async Task StartAsync()
        {
            _process.Start();
            _process.BeginErrorReadLine();
            _input = _process.StandardInput;
            _output = _process.StandardOutput;
            _cts = new CancellationTokenSource();

            _ = Task.Run(ReadLoopAsync);
        }

        private async Task ReadLoopAsync()
        {
            try
            {
                while (!_cts.Token.IsCancellationRequested && !_process.HasExited)
                {
                    string line = await _output.ReadLineAsync();
                    if (line != null)
                    {
                        OnMessageReceived?.Invoke(line);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[MCP Read Error] {ex.Message}");
            }
        }

        public async Task SendAsync(string message)
        {
            if (_input != null)
            {
                await _input.WriteLineAsync(message);
                await _input.FlushAsync();
            }
        }

        public void Dispose()
        {
            _cts?.Cancel();
            if (_process != null && !_process.HasExited)
            {
                _process.Kill();
            }
            _process?.Dispose();
        }
    }
}
