using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using WpfBrushes = System.Windows.Media.Brushes;
using Autodesk.Revit.UI;
using BAC_MCP.Core;
using BAC_MCP.Mcp;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace BAC_MCP.UI
{
    public partial class McpDockablePane : Page, IDockablePaneProvider
    {
        private McpClient? _client;
        private StdioTransport? _transport;
        private CancellationTokenSource? _operationCts;

        private List<McpTool> _tools = new();
        private List<McpResource> _resources = new();
        private List<McpPrompt> _prompts = new();

        private List<string> _commandHistory = new();
        private int _historyIndex = -1;

        private readonly Settings _settings;

        public McpDockablePane()
        {
            InitializeComponent();

            Logger.Initialize();
            Logger.Info("McpDockablePane initialized");

            _settings = Settings.Instance;
            _commandHistory = _settings.CommandHistory.ToList();

            RestoreLastConfiguration();
            UpdateUIState(false);
        }

        public void SetupDockablePane(DockablePaneProviderData data)
        {
            data.FrameworkElement = this as FrameworkElement;
            data.InitialState = new DockablePaneState
            {
                DockPosition = DockPosition.Right,
            };
        }

        #region Configuration Persistence

        private void RestoreLastConfiguration()
        {
            try
            {
                if (_settings.LastServerIndex >= 0 && _settings.LastServerIndex < ServerSelector.Items.Count)
                {
                    ServerSelector.SelectedIndex = _settings.LastServerIndex;
                }

                if (_settings.LastCustomServer != null)
                {
                    CustomCommandType.SelectedIndex = _settings.LastCustomServer.CommandType;
                    CustomServerCommand.Text = _settings.LastCustomServer.Command;
                    CustomServerArgs.Text = _settings.LastCustomServer.Arguments;
                    CustomServerEnv.Text = FormatEnvVars(_settings.LastCustomServer.EnvironmentVariables);
                }

                Logger.Debug("Configuration restored");
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to restore configuration", ex);
            }
        }

        private void SaveCurrentConfiguration()
        {
            try
            {
                _settings.LastServerIndex = ServerSelector.SelectedIndex;

                if (CustomServerPanel.Visibility == Visibility.Visible)
                {
                    _settings.LastCustomServer = new ServerProfile
                    {
                        Name = GetServerDisplayName(),
                        CommandType = CustomCommandType.SelectedIndex,
                        Command = CustomServerCommand.Text.Trim(),
                        Arguments = CustomServerArgs.Text.Trim(),
                        EnvironmentVariables = ParseEnvVars(CustomServerEnv.Text),
                        LastUsed = DateTime.Now
                    };
                }

                _settings.Save();
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to save configuration", ex);
            }
        }

        private string FormatEnvVars(Dictionary<string, string> vars)
        {
            return string.Join("\r\n", vars.Select(kv => $"{kv.Key}={kv.Value}"));
        }

        private Dictionary<string, string> ParseEnvVars(string text)
        {
            var vars = new Dictionary<string, string>();
            if (string.IsNullOrWhiteSpace(text)) return vars;

            foreach (var line in text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var parts = line.Split(new[] { '=' }, 2);
                if (parts.Length == 2)
                {
                    vars[parts[0].Trim()] = parts[1].Trim();
                }
            }
            return vars;
        }

        #endregion

        #region UI State Management

        private void UpdateUIState(bool connected)
        {
            // Connection controls
            ServerSelector.IsEnabled = !connected;
            CustomServerPanel.IsEnabled = !connected;
            ConnectBtn.Content = connected ? "Disconnect" : "Connect";

            // Status indicator
            StatusIndicator.Fill = connected ? WpfBrushes.Green : WpfBrushes.Red;
            StatusText.Text = connected ? "Connected" : "Disconnected";

            // Tools tab
            RefreshToolsBtn.IsEnabled = connected;
            ExecuteToolBtn.IsEnabled = connected && ToolsList.SelectedItem != null;
            ArgumentsBox.IsEnabled = connected;
            ToolsList.IsEnabled = connected;

            // Resources tab
            RefreshResourcesBtn.IsEnabled = connected;
            ReadResourceBtn.IsEnabled = connected && ResourcesList.SelectedItem != null;
            ResourcesList.IsEnabled = connected;

            // Prompts tab
            RefreshPromptsBtn.IsEnabled = connected;
            GetPromptBtn.IsEnabled = connected && PromptsList.SelectedItem != null;
            PromptArgumentsBox.IsEnabled = connected;
            PromptsList.IsEnabled = connected;

            if (!connected)
            {
                ClearAllLists();
            }
        }

        private void ClearAllLists()
        {
            _tools.Clear();
            _resources.Clear();
            _prompts.Clear();

            ToolsList.ItemsSource = null;
            ResourcesList.ItemsSource = null;
            PromptsList.ItemsSource = null;

            ToolDescription.Text = "";
            ArgumentsBox.Text = "";
            ResourceDescription.Text = "";
            ResourceContent.Text = "";
            PromptDescription.Text = "";
            PromptArgumentsBox.Text = "";
            PromptMessages.Text = "";
        }

        private void ShowProgress(string message)
        {
            ProgressText.Text = message;
            ProgressOverlay.Visibility = Visibility.Visible;
        }

        private void HideProgress()
        {
            ProgressOverlay.Visibility = Visibility.Collapsed;
        }

        #endregion

        #region Server Selection

        private void ServerSelector_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (CustomServerPanel == null) return;

            string? serverName = (ServerSelector.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (serverName == null) return;

            bool isConfigurable = serverName.Contains("Custom") ||
                                  serverName.Contains("Filesystem") ||
                                  serverName.Contains("Airtable") ||
                                  serverName.Contains("n8n") ||
                                  serverName.Contains("SQLite") ||
                                  serverName.Contains("PostgreSQL") ||
                                  serverName.Contains("Brave Search");

            CustomServerPanel.Visibility = isConfigurable ? Visibility.Visible : Visibility.Collapsed;

            SetServerDefaults(serverName);
        }

        private void SetServerDefaults(string serverName)
        {
            switch (serverName)
            {
                case var s when s.Contains("Filesystem"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "@modelcontextprotocol/server-filesystem";
                    CustomServerArgs.Text = "C:\\Users";
                    CustomServerEnv.Text = "";
                    break;

                case var s when s.Contains("Airtable"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "airtable-mcp-server";
                    CustomServerArgs.Text = "";
                    CustomServerEnv.Text = "AIRTABLE_API_KEY=";
                    break;

                case var s when s.Contains("n8n"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "n8n-mcp";
                    CustomServerArgs.Text = "";
                    CustomServerEnv.Text = "N8N_API_KEY=\r\nN8N_HOST=https://your-n8n-instance.com";
                    break;

                case var s when s.Contains("Brave Search"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "@modelcontextprotocol/server-brave-search";
                    CustomServerArgs.Text = "";
                    CustomServerEnv.Text = "BRAVE_API_KEY=";
                    break;

                case var s when s.Contains("SQLite"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "@modelcontextprotocol/server-sqlite";
                    CustomServerArgs.Text = "C:\\path\\to\\database.db";
                    CustomServerEnv.Text = "";
                    break;

                case var s when s.Contains("PostgreSQL"):
                    CustomCommandType.SelectedIndex = 0;
                    CustomServerCommand.Text = "@modelcontextprotocol/server-postgres";
                    CustomServerArgs.Text = "";
                    CustomServerEnv.Text = "POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/db";
                    break;
            }
        }

        private (string command, string args, Dictionary<string, string>? envVars) BuildServerCommand()
        {
            string? serverName = (ServerSelector.SelectedItem as ComboBoxItem)?.Content.ToString();

            return serverName switch
            {
                var s when s?.Contains("Github") == true =>
                    ("cmd.exe", "/c npx -y @modelcontextprotocol/server-github", null),

                var s when s?.Contains("Google Maps") == true =>
                    ("cmd.exe", "/c npx -y @modelcontextprotocol/server-google-maps", null),

                var s when s?.Contains("Puppeteer") == true =>
                    ("cmd.exe", "/c npx -y @modelcontextprotocol/server-puppeteer", null),

                var s when s?.Contains("Memory") == true =>
                    ("cmd.exe", "/c npx -y @modelcontextprotocol/server-memory", null),

                var s when s?.Contains("Sequential Thinking") == true =>
                    ("cmd.exe", "/c npx -y @modelcontextprotocol/server-sequential-thinking", null),

                _ => BuildCustomServerCommand()
            };
        }

        private (string command, string args, Dictionary<string, string>? envVars) BuildCustomServerCommand()
        {
            string package = CustomServerCommand.Text.Trim();
            string extraArgs = CustomServerArgs.Text.Trim();
            string envText = CustomServerEnv.Text.Trim();

            if (string.IsNullOrEmpty(package))
            {
                throw new ArgumentException("Package/Script/Path is required.");
            }

            var envVars = ParseEnvVars(envText);
            if (envVars.Count == 0) envVars = null!;

            int commandType = CustomCommandType.SelectedIndex;
            string command, args;

            switch (commandType)
            {
                case 0: // npx
                    command = "cmd.exe";
                    args = $"/c npx -y {package}";
                    if (!string.IsNullOrEmpty(extraArgs)) args += $" {extraArgs}";
                    break;

                case 1: // node
                    command = "cmd.exe";
                    args = $"/c node \"{package}\"";
                    if (!string.IsNullOrEmpty(extraArgs)) args += $" {extraArgs}";
                    break;

                case 2: // python
                    command = "cmd.exe";
                    args = $"/c python \"{package}\"";
                    if (!string.IsNullOrEmpty(extraArgs)) args += $" {extraArgs}";
                    break;

                case 3: // Custom executable
                    command = package;
                    args = extraArgs;
                    break;

                default:
                    throw new ArgumentException("Invalid command type.");
            }

            return (command, args, envVars);
        }

        private string GetServerDisplayName()
        {
            if (ServerSelector.SelectedItem is ComboBoxItem item)
            {
                string content = item.Content.ToString() ?? "";
                if (content.Contains("Custom") && !string.IsNullOrEmpty(CustomServerCommand.Text))
                {
                    return CustomServerCommand.Text.Trim();
                }
                return content;
            }
            return "Unknown Server";
        }

        #endregion

        #region Connection

        private async void ConnectBtn_Click(object sender, RoutedEventArgs e)
        {
            if (_client != null)
            {
                Disconnect();
                return;
            }

            try
            {
                ShowProgress("Connecting...");
                ConnectBtn.IsEnabled = false;

                var (command, args, envVars) = BuildServerCommand();
                string displayName = GetServerDisplayName();

                Logger.Info($"Connecting to: {displayName}");
                AppendOutput($"Starting: {command} {args}");

                _transport = new StdioTransport(command, args, envVars);
                _transport.OnErrorReceived += msg => Dispatcher.Invoke(() =>
                {
                    Logger.Debug($"[stderr] {msg}");
                    AppendOutput($"[stderr] {msg}");
                });

                _client = new McpClient(_transport);
                _client.DefaultTimeoutMs = _settings.DefaultTimeoutMs;
                _client.OnNotification += notification => Dispatcher.Invoke(() =>
                {
                    Logger.Debug($"Notification: {notification}");
                    if (notification.Contains("tools/list_changed"))
                        _ = LoadToolsAsync();
                    else if (notification.Contains("resources/list_changed"))
                        _ = LoadResourcesAsync();
                    else if (notification.Contains("prompts/list_changed"))
                        _ = LoadPromptsAsync();
                });

                _operationCts = new CancellationTokenSource();
                await _client.ConnectAsync(_operationCts.Token);

                SaveCurrentConfiguration();
                UpdateUIState(true);
                AppendOutput($"Connected to {displayName}");
                Logger.Info($"Connected to {displayName}");

                // Load all data
                await LoadToolsAsync();
                await LoadResourcesAsync();
                await LoadPromptsAsync();
            }
            catch (OperationCanceledException)
            {
                AppendOutput("Connection cancelled.");
            }
            catch (Exception ex)
            {
                Logger.Error("Connection failed", ex);
                AppendOutput($"Connection Error: {ex.Message}");
                Disconnect();
            }
            finally
            {
                HideProgress();
                ConnectBtn.IsEnabled = true;
            }
        }

        private void Disconnect()
        {
            try
            {
                _operationCts?.Cancel();
                _client?.Dispose();
                _transport?.Dispose();
            }
            catch (Exception ex)
            {
                Logger.Error("Error during disconnect", ex);
            }
            finally
            {
                _client = null;
                _transport = null;
                _operationCts = null;

                UpdateUIState(false);
                AppendOutput("Disconnected");
                Logger.Info("Disconnected");
            }
        }

        private void CancelOperationBtn_Click(object sender, RoutedEventArgs e)
        {
            _operationCts?.Cancel();
            _client?.CancelAllPendingRequests();
            HideProgress();
            AppendOutput("Operation cancelled.");
        }

        #endregion

        #region Tools

        private async void RefreshToolsBtn_Click(object sender, RoutedEventArgs e)
        {
            await LoadToolsAsync();
        }

        private async System.Threading.Tasks.Task LoadToolsAsync()
        {
            if (_client == null) return;

            try
            {
                AppendOutput("Loading tools...");
                var result = await _client.ListToolsAsync(_operationCts?.Token ?? default);

                _tools.Clear();
                if (result["tools"] is JArray toolsArray)
                {
                    foreach (var tool in toolsArray)
                    {
                        var mcpTool = tool.ToObject<McpTool>();
                        if (mcpTool != null) _tools.Add(mcpTool);
                    }
                }

                ToolsList.ItemsSource = null;
                ToolsList.ItemsSource = _tools;
                AppendOutput($"Loaded {_tools.Count} tools");
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to load tools", ex);
                AppendOutput($"Error loading tools: {ex.Message}");
            }
        }

        private void ToolsList_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ToolsList.SelectedItem is McpTool selectedTool)
            {
                ToolDescription.Text = selectedTool.Description;
                ArgumentsBox.Text = selectedTool.GetArgumentsTemplate();
                ExecuteToolBtn.IsEnabled = true;
            }
            else
            {
                ToolDescription.Text = "";
                ArgumentsBox.Text = "";
                ExecuteToolBtn.IsEnabled = false;
            }
        }

        private async void ExecuteToolBtn_Click(object sender, RoutedEventArgs e)
        {
            if (_client == null || ToolsList.SelectedItem is not McpTool selectedTool) return;

            try
            {
                ShowProgress($"Executing {selectedTool.Name}...");
                ExecuteToolBtn.IsEnabled = false;

                string argsText = ArgumentsBox.Text.Trim();
                JObject arguments;

                if (string.IsNullOrEmpty(argsText) || argsText == "{}")
                {
                    arguments = new JObject();
                }
                else
                {
                    arguments = JObject.Parse(argsText);
                }

                // Validate arguments
                var validation = SchemaValidator.Validate(arguments, selectedTool.InputSchema);
                if (!validation.IsValid)
                {
                    AppendOutput("Validation Errors:");
                    AppendOutput(validation.GetErrorSummary());
                    return;
                }

                if (validation.Warnings.Count > 0)
                {
                    foreach (var warning in validation.Warnings)
                        AppendOutput($"Warning: {warning}");
                }

                AppendOutput($"Executing: {selectedTool.Name}");
                Logger.Info($"Executing tool: {selectedTool.Name}");

                var result = await _client.CallToolAsync(selectedTool.Name, arguments,
                    _operationCts?.Token ?? default);

                AppendOutput("--- Result ---");
                AppendOutput(result?.ToString(Formatting.Indented) ?? "No result");
            }
            catch (JsonException)
            {
                AppendOutput("Error: Invalid JSON in arguments.");
            }
            catch (TimeoutException ex)
            {
                AppendOutput($"Timeout: {ex.Message}");
            }
            catch (McpException ex)
            {
                AppendOutput($"MCP Error: {ex.GetUserFriendlyMessage()}");
            }
            catch (OperationCanceledException)
            {
                AppendOutput("Execution cancelled.");
            }
            catch (Exception ex)
            {
                Logger.Error("Tool execution failed", ex);
                AppendOutput($"Error: {ex.Message}");
            }
            finally
            {
                HideProgress();
                ExecuteToolBtn.IsEnabled = true;
            }
        }

        #endregion

        #region Resources

        private async void RefreshResourcesBtn_Click(object sender, RoutedEventArgs e)
        {
            await LoadResourcesAsync();
        }

        private async System.Threading.Tasks.Task LoadResourcesAsync()
        {
            if (_client == null) return;

            try
            {
                var result = await _client.ListResourcesAsync(_operationCts?.Token ?? default);

                _resources.Clear();
                if (result["resources"] is JArray resourcesArray)
                {
                    foreach (var resource in resourcesArray)
                    {
                        var mcpResource = resource.ToObject<McpResource>();
                        if (mcpResource != null) _resources.Add(mcpResource);
                    }
                }

                ResourcesList.ItemsSource = null;
                ResourcesList.ItemsSource = _resources;
            }
            catch (McpException ex) when (ex.Message.Contains("Method Not Found"))
            {
                // Server doesn't support resources
                _resources.Clear();
                ResourcesList.ItemsSource = null;
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to load resources", ex);
            }
        }

        private void ResourcesList_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ResourcesList.SelectedItem is McpResource selected)
            {
                ResourceDescription.Text = selected.Description ?? selected.Uri;
                ReadResourceBtn.IsEnabled = true;
            }
            else
            {
                ResourceDescription.Text = "";
                ReadResourceBtn.IsEnabled = false;
            }
        }

        private async void ReadResourceBtn_Click(object sender, RoutedEventArgs e)
        {
            if (_client == null || ResourcesList.SelectedItem is not McpResource selected) return;

            try
            {
                ShowProgress("Reading resource...");
                ReadResourceBtn.IsEnabled = false;

                var result = await _client.ReadResourceAsync(selected.Uri, _operationCts?.Token ?? default);

                var contents = result["contents"]?.First;
                if (contents != null)
                {
                    var content = contents.ToObject<McpResourceContent>();
                    ResourceContent.Text = content?.GetDisplayContent() ?? "No content";
                }
                else
                {
                    ResourceContent.Text = result?.ToString(Formatting.Indented) ?? "No content";
                }
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to read resource", ex);
                ResourceContent.Text = $"Error: {ex.Message}";
            }
            finally
            {
                HideProgress();
                ReadResourceBtn.IsEnabled = true;
            }
        }

        #endregion

        #region Prompts

        private async void RefreshPromptsBtn_Click(object sender, RoutedEventArgs e)
        {
            await LoadPromptsAsync();
        }

        private async System.Threading.Tasks.Task LoadPromptsAsync()
        {
            if (_client == null) return;

            try
            {
                var result = await _client.ListPromptsAsync(_operationCts?.Token ?? default);

                _prompts.Clear();
                if (result["prompts"] is JArray promptsArray)
                {
                    foreach (var prompt in promptsArray)
                    {
                        var mcpPrompt = prompt.ToObject<McpPrompt>();
                        if (mcpPrompt != null) _prompts.Add(mcpPrompt);
                    }
                }

                PromptsList.ItemsSource = null;
                PromptsList.ItemsSource = _prompts;
            }
            catch (McpException ex) when (ex.Message.Contains("Method Not Found"))
            {
                // Server doesn't support prompts
                _prompts.Clear();
                PromptsList.ItemsSource = null;
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to load prompts", ex);
            }
        }

        private void PromptsList_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (PromptsList.SelectedItem is McpPrompt selected)
            {
                PromptDescription.Text = selected.Description ?? "";
                PromptArgumentsBox.Text = selected.GetArgumentsTemplate();
                GetPromptBtn.IsEnabled = true;
            }
            else
            {
                PromptDescription.Text = "";
                PromptArgumentsBox.Text = "";
                GetPromptBtn.IsEnabled = false;
            }
        }

        private async void GetPromptBtn_Click(object sender, RoutedEventArgs e)
        {
            if (_client == null || PromptsList.SelectedItem is not McpPrompt selected) return;

            try
            {
                ShowProgress("Getting prompt...");
                GetPromptBtn.IsEnabled = false;

                string argsText = PromptArgumentsBox.Text.Trim();
                object? arguments = null;

                if (!string.IsNullOrEmpty(argsText) && argsText != "{}")
                {
                    arguments = JObject.Parse(argsText);
                }

                var result = await _client.GetPromptAsync(selected.Name, arguments,
                    _operationCts?.Token ?? default);

                if (result["messages"] is JArray messages)
                {
                    var output = new System.Text.StringBuilder();
                    foreach (var msg in messages)
                    {
                        string role = msg["role"]?.Value<string>() ?? "unknown";
                        var content = msg["content"];

                        output.AppendLine($"[{role}]");

                        if (content?["text"] != null)
                        {
                            output.AppendLine(content["text"]?.Value<string>());
                        }
                        else
                        {
                            output.AppendLine(content?.ToString(Formatting.Indented));
                        }
                        output.AppendLine();
                    }
                    PromptMessages.Text = output.ToString();
                }
                else
                {
                    PromptMessages.Text = result?.ToString(Formatting.Indented) ?? "No messages";
                }
            }
            catch (JsonException)
            {
                PromptMessages.Text = "Error: Invalid JSON in arguments.";
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to get prompt", ex);
                PromptMessages.Text = $"Error: {ex.Message}";
            }
            finally
            {
                HideProgress();
                GetPromptBtn.IsEnabled = true;
            }
        }

        #endregion

        #region Command Input

        private void InputBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == Key.Up)
            {
                NavigateHistory(1);
                e.Handled = true;
            }
            else if (e.Key == Key.Down)
            {
                NavigateHistory(-1);
                e.Handled = true;
            }
            else if (e.Key == Key.Enter)
            {
                SendBtn_Click(sender, e);
                e.Handled = true;
            }
        }

        private void NavigateHistory(int direction)
        {
            if (_commandHistory.Count == 0) return;

            int newIndex = _historyIndex + direction;

            if (newIndex < -1) newIndex = -1;
            if (newIndex >= _commandHistory.Count) newIndex = _commandHistory.Count - 1;

            _historyIndex = newIndex;

            if (_historyIndex == -1)
            {
                InputBox.Text = "";
            }
            else
            {
                InputBox.Text = _commandHistory[_commandHistory.Count - 1 - _historyIndex];
                InputBox.CaretIndex = InputBox.Text.Length;
            }
        }

        private async void SendBtn_Click(object sender, RoutedEventArgs e)
        {
            if (_client == null)
            {
                AppendOutput("Not connected.");
                return;
            }

            string input = InputBox.Text.Trim();
            if (string.IsNullOrEmpty(input)) return;

            // Add to history
            if (_commandHistory.Count == 0 || _commandHistory.Last() != input)
            {
                _settings.AddToCommandHistory(input);
                _commandHistory = _settings.CommandHistory.ToList();
            }
            _historyIndex = -1;

            AppendOutput($"> {input}");
            InputBox.Text = "";

            try
            {
                string inputLower = input.ToLower();

                if (inputLower == "list tools" || inputLower == "list")
                {
                    await LoadToolsAsync();
                }
                else if (inputLower == "list resources")
                {
                    await LoadResourcesAsync();
                }
                else if (inputLower == "list prompts")
                {
                    await LoadPromptsAsync();
                }
                else if (inputLower.StartsWith("call "))
                {
                    await ProcessCallCommand(input.Substring(5).Trim());
                }
                else if (inputLower.StartsWith("read "))
                {
                    await ProcessReadCommand(input.Substring(5).Trim());
                }
                else if (inputLower == "help")
                {
                    ShowHelp();
                }
                else
                {
                    AppendOutput("Unknown command. Type 'help' for available commands.");
                }
            }
            catch (Exception ex)
            {
                AppendOutput($"Error: {ex.Message}");
            }
        }

        private async System.Threading.Tasks.Task ProcessCallCommand(string command)
        {
            if (_client == null) return;

            var match = Regex.Match(command, @"^(\S+)\s*(.*)$");
            if (!match.Success)
            {
                AppendOutput("Usage: call <tool_name> {\"arg\":\"value\"}");
                return;
            }

            string toolName = match.Groups[1].Value;
            string argsJson = match.Groups[2].Value.Trim();

            object arguments;
            if (string.IsNullOrEmpty(argsJson))
            {
                arguments = new { };
            }
            else
            {
                try
                {
                    arguments = JObject.Parse(argsJson);
                }
                catch (JsonException)
                {
                    AppendOutput("Error: Invalid JSON arguments.");
                    return;
                }
            }

            AppendOutput($"Calling: {toolName}");
            var result = await _client.CallToolAsync(toolName, arguments, _operationCts?.Token ?? default);
            AppendOutput("--- Result ---");
            AppendOutput(result?.ToString(Formatting.Indented) ?? "No result");
        }

        private async System.Threading.Tasks.Task ProcessReadCommand(string uri)
        {
            if (_client == null || string.IsNullOrEmpty(uri)) return;

            AppendOutput($"Reading: {uri}");
            var result = await _client.ReadResourceAsync(uri, _operationCts?.Token ?? default);

            var contents = result["contents"]?.First;
            if (contents != null)
            {
                var content = contents.ToObject<McpResourceContent>();
                AppendOutput("--- Content ---");
                AppendOutput(content?.GetDisplayContent() ?? "No content");
            }
            else
            {
                AppendOutput(result?.ToString(Formatting.Indented) ?? "No content");
            }
        }

        private void ShowHelp()
        {
            AppendOutput("=== Available Commands ===");
            AppendOutput("list tools     - List available tools");
            AppendOutput("list resources - List available resources");
            AppendOutput("list prompts   - List available prompts");
            AppendOutput("call <name> <json> - Execute a tool");
            AppendOutput("read <uri>     - Read a resource");
            AppendOutput("help           - Show this help");
            AppendOutput("");
            AppendOutput("Use Up/Down arrows for command history.");
        }

        #endregion

        #region Output

        private void ClearOutputBtn_Click(object sender, RoutedEventArgs e)
        {
            OutputText.Text = "";
        }

        private void AppendOutput(string text)
        {
            OutputText.Text += $"{text}\n";
            OutputScroller?.ScrollToBottom();
        }

        #endregion
    }
}
