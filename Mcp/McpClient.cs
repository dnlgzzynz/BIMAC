using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using BAC_MCP.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace BAC_MCP.Mcp
{
    public class McpClient : IDisposable
    {
        private readonly StdioTransport _transport;
        private int _requestId = 0;
        private readonly ConcurrentDictionary<int, TaskCompletionSource<JToken>> _pendingRequests = new();

        private int _defaultTimeoutMs = 30000;
        private bool _disposed = false;

        public event Action<string>? OnNotification;
        public event Action<string, JToken?>? OnResourceUpdated;

        public int DefaultTimeoutMs
        {
            get => _defaultTimeoutMs;
            set => _defaultTimeoutMs = value > 0 ? value : 30000;
        }

        public bool IsConnected => _transport != null && !_disposed;

        public McpClient(StdioTransport transport)
        {
            _transport = transport ?? throw new ArgumentNullException(nameof(transport));
            _transport.OnMessageReceived += HandleMessage;
        }

        public async Task ConnectAsync(CancellationToken cancellationToken = default)
        {
            Logger.Info("Starting MCP connection...");

            await _transport.StartAsync();

            // Initialize handshake
            var initParams = new
            {
                protocolVersion = "2024-11-05",
                capabilities = new
                {
                    roots = new { listChanged = true },
                    sampling = new { }
                },
                clientInfo = new { name = "BAC_MCP_Revit", version = "1.0.0" }
            };

            var result = await SendRequestAsync("initialize", initParams, cancellationToken);
            Logger.Info($"MCP initialized. Server capabilities received.");

            await SendNotificationAsync("notifications/initialized", new { });
            Logger.Info("MCP connection established.");
        }

        public async Task<JToken> CallToolAsync(string toolName, object arguments,
            CancellationToken cancellationToken = default, int? timeoutMs = null)
        {
            Logger.Info($"Calling tool: {toolName}");

            var parameters = new
            {
                name = toolName,
                arguments = arguments
            };

            return await SendRequestAsync("tools/call", parameters, cancellationToken, timeoutMs);
        }

        public async Task<JToken> ListToolsAsync(CancellationToken cancellationToken = default)
        {
            Logger.Debug("Listing tools...");
            return await SendRequestAsync("tools/list", new { }, cancellationToken);
        }

        public async Task<JToken> ListResourcesAsync(CancellationToken cancellationToken = default)
        {
            Logger.Debug("Listing resources...");
            return await SendRequestAsync("resources/list", new { }, cancellationToken);
        }

        public async Task<JToken> ReadResourceAsync(string uri, CancellationToken cancellationToken = default)
        {
            Logger.Debug($"Reading resource: {uri}");
            return await SendRequestAsync("resources/read", new { uri }, cancellationToken);
        }

        public async Task<JToken> ListPromptsAsync(CancellationToken cancellationToken = default)
        {
            Logger.Debug("Listing prompts...");
            return await SendRequestAsync("prompts/list", new { }, cancellationToken);
        }

        public async Task<JToken> GetPromptAsync(string name, object? arguments = null,
            CancellationToken cancellationToken = default)
        {
            Logger.Debug($"Getting prompt: {name}");
            var parameters = new { name, arguments = arguments ?? new { } };
            return await SendRequestAsync("prompts/get", parameters, cancellationToken);
        }

        private async Task<JToken> SendRequestAsync(string method, object parameters,
            CancellationToken cancellationToken = default, int? timeoutMs = null)
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(McpClient));

            int id = Interlocked.Increment(ref _requestId);
            var tcs = new TaskCompletionSource<JToken>(TaskCreationOptions.RunContinuationsAsynchronously);
            _pendingRequests[id] = tcs;

            Logger.McpRequest(method, id);

            // Create linked cancellation token with timeout
            int timeout = timeoutMs ?? _defaultTimeoutMs;
            using var timeoutCts = new CancellationTokenSource(timeout);
            using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
                cancellationToken, timeoutCts.Token);

            // Register cancellation callback
            using var registration = linkedCts.Token.Register(() =>
            {
                if (_pendingRequests.TryRemove(id, out var pendingTcs))
                {
                    if (timeoutCts.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
                    {
                        Logger.Warning($"Request {id} ({method}) timed out after {timeout}ms");
                        pendingTcs.TrySetException(new TimeoutException(
                            $"Request '{method}' timed out after {timeout}ms"));
                    }
                    else
                    {
                        Logger.Debug($"Request {id} ({method}) cancelled");
                        pendingTcs.TrySetCanceled(cancellationToken);
                    }
                }
            });

            var request = new
            {
                jsonrpc = "2.0",
                id = id,
                method = method,
                @params = parameters
            };

            string json = JsonConvert.SerializeObject(request);

            try
            {
                await _transport.SendAsync(json);
                return await tcs.Task;
            }
            catch (OperationCanceledException) when (timeoutCts.IsCancellationRequested)
            {
                throw new TimeoutException($"Request '{method}' timed out after {timeout}ms");
            }
        }

        private async Task SendNotificationAsync(string method, object parameters)
        {
            if (_disposed) return;

            var notification = new
            {
                jsonrpc = "2.0",
                method = method,
                @params = parameters
            };

            string json = JsonConvert.SerializeObject(notification);
            await _transport.SendAsync(json);

            Logger.Debug($"Sent notification: {method}");
        }

        public void CancelAllPendingRequests()
        {
            Logger.Info($"Cancelling {_pendingRequests.Count} pending requests");

            foreach (var kvp in _pendingRequests)
            {
                if (_pendingRequests.TryRemove(kvp.Key, out var tcs))
                {
                    tcs.TrySetCanceled();
                }
            }
        }

        public int PendingRequestCount => _pendingRequests.Count;

        private void HandleMessage(string message)
        {
            try
            {
                JObject json = JObject.Parse(message);

                // Handle Response (has id)
                if (json.ContainsKey("id") && json["id"]?.Type != JTokenType.Null)
                {
                    int id = json["id"]!.Value<int>();

                    if (_pendingRequests.TryRemove(id, out var tcs))
                    {
                        if (json.ContainsKey("error") && json["error"]?.Type != JTokenType.Null)
                        {
                            var error = json["error"]!;
                            int? code = error["code"]?.Value<int>();
                            string errorMessage = error["message"]?.Value<string>() ?? "Unknown error";

                            Logger.McpResponse(id, false, errorMessage);
                            tcs.SetException(new McpException(errorMessage, code, error["data"]));
                        }
                        else
                        {
                            Logger.McpResponse(id, true);
                            tcs.SetResult(json["result"] ?? JValue.CreateNull());
                        }
                    }
                }
                // Handle Notifications (no id, has method)
                else if (json.ContainsKey("method"))
                {
                    string? method = json["method"]?.Value<string>();
                    var parameters = json["params"];

                    Logger.Debug($"Received notification: {method}");

                    switch (method)
                    {
                        case "notifications/resources/updated":
                            string? uri = parameters?["uri"]?.Value<string>();
                            if (uri != null)
                            {
                                OnResourceUpdated?.Invoke(uri, parameters);
                            }
                            break;

                        case "notifications/resources/list_changed":
                        case "notifications/tools/list_changed":
                        case "notifications/prompts/list_changed":
                            OnNotification?.Invoke(method);
                            break;

                        default:
                            OnNotification?.Invoke(method ?? "unknown");
                            break;
                    }
                }
            }
            catch (JsonException ex)
            {
                Logger.Error("Failed to parse MCP message", ex);
            }
            catch (Exception ex)
            {
                Logger.Error("Error handling MCP message", ex);
            }
        }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;

            Logger.Info("Disposing MCP client");
            CancelAllPendingRequests();
            _transport.OnMessageReceived -= HandleMessage;
        }
    }
}
