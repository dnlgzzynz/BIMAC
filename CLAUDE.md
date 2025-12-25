# CLAUDE.md - BAC_MCP Project Guide

This document serves as a comprehensive guide for AI assistants working on the BAC_MCP project.

## Project Overview

**BAC_MCP** is a Revit 2026 add-in that implements a Model Context Protocol (MCP) client, enabling communication with external MCP servers directly from within Revit.

- **Framework:** .NET 8.0 Windows
- **Language:** C# (latest)
- **UI Framework:** WPF
- **Target Platform:** x64
- **Revit Version:** 2026

## Repository Structure

```
BAC_MCP/
├── App.cs                      # Plugin entry point (IExternalApplication)
├── BAC_MCP.csproj              # Project configuration
├── BAC_MCP.sln                 # Visual Studio solution
├── Commands/
│   └── OpenAssistantCommand.cs # Ribbon button command (IExternalCommand)
├── Core/
│   ├── Logger.cs               # File-based logging system
│   ├── Settings.cs             # Persistent configuration management
│   └── ServerProfile.cs        # Server profile data model
├── Mcp/
│   ├── McpClient.cs            # MCP client - JSON-RPC with timeout/cancellation
│   ├── McpException.cs         # Typed MCP exceptions
│   ├── McpPrompt.cs            # Prompt data models
│   ├── McpResource.cs          # Resource data models
│   ├── McpTool.cs              # Tool data models
│   ├── SchemaValidator.cs      # JSON schema validation
│   └── StdioTransport.cs       # Stdio transport layer
├── UI/
│   ├── McpDockablePane.xaml    # WPF interface with tabs
│   └── McpDockablePane.xaml.cs # UI code-behind
├── bin/                        # Compiled binaries
└── obj/                        # Build intermediates
```

## Architecture

### Layer Overview

```
┌─────────────────────────────────────┐
│          Revit Integration          │
│    (App.cs, OpenAssistantCommand)   │
├─────────────────────────────────────┤
│           UI Layer (WPF)            │
│         (McpDockablePane)           │
├─────────────────────────────────────┤
│          MCP Client Layer           │
│           (McpClient)               │
├─────────────────────────────────────┤
│         Transport Layer             │
│        (StdioTransport)             │
└─────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| StdioTransport | `Mcp/StdioTransport.cs` | Spawns MCP server process, handles stdin/stdout communication |
| McpClient | `Mcp/McpClient.cs` | JSON-RPC 2.0 client, MCP protocol implementation |
| McpTool | `Mcp/McpTool.cs` | Data models for MCP tools and schemas |
| McpDockablePane | `UI/McpDockablePane.xaml(.cs)` | Main user interface as Revit DockablePane |
| App | `App.cs` | Plugin initialization, ribbon setup |
| OpenAssistantCommand | `Commands/OpenAssistantCommand.cs` | Opens the MCP panel |

## MCP Protocol Details

- **Protocol Version:** 2024-11-05
- **Transport:** stdio (stdin/stdout)
- **Message Format:** JSON-RPC 2.0

### Supported Operations

- `initialize` - Handshake with MCP server
- `tools/list` - List available tools
- `tools/call` - Execute a tool with arguments
- `resources/list` - List available resources
- `resources/read` - Read resource content
- `prompts/list` - List available prompts
- `prompts/get` - Get prompt with arguments

## Development Guidelines

### Code Style

- Use C# latest language features
- Enable nullable reference types (`#nullable enable`)
- Use async/await for all I/O operations
- Follow Microsoft C# naming conventions:
  - `PascalCase` for public members, types, methods
  - `_camelCase` for private fields
  - `camelCase` for local variables and parameters

### Revit API Considerations

- All UI operations must run on the main thread
- Use `Dispatcher.Invoke()` when updating UI from async callbacks
- External commands execute in a valid Revit API context
- DockablePane registration happens in `OnStartup()`

### Adding New MCP Servers

To add a predefined MCP server:

1. Add a new `ComboBoxItem` in `McpDockablePane.xaml` ServerSelector
2. Update `BuildServerCommand()` in `McpDockablePane.xaml.cs` with the command configuration
3. Include any required environment variables

### Error Handling

- Wrap MCP operations in try-catch blocks
- Display errors in the OutputText area
- Log transport errors via the `ErrorReceived` event

## Build & Deploy

### Build Commands

```bash
# Build the project
dotnet build BAC_MCP.csproj

# Build Release
dotnet build BAC_MCP.csproj -c Release
```

### Revit Add-in Installation

The compiled DLL must be registered with Revit via a `.addin` manifest file in:
- `%APPDATA%\Autodesk\Revit\Addins\2026\`

## Dependencies

### NuGet Packages

- `Newtonsoft.Json` 13.0.3 - JSON serialization

### Revit API References

- `RevitAPI.dll` - Core Revit API
- `RevitAPIUI.dll` - Revit UI API

Located at: `C:\Program Files\Autodesk\Revit 2026\`

## Testing

Currently no automated tests. Manual testing workflow:

1. Build the project
2. Copy DLL to Revit addins folder
3. Launch Revit 2026
4. Open BAC MCP panel from ribbon
5. Connect to an MCP server
6. Test tool listing and execution

## Features

- **Logging:** File-based logging to `%LOCALAPPDATA%/BAC_MCP/logs/`
- **Persistence:** Configuration saved to `%LOCALAPPDATA%/BAC_MCP/settings.json`
- **Command History:** Navigate with Up/Down arrows, persisted between sessions
- **Timeouts:** Configurable request timeout (default 30s)
- **Cancellation:** Cancel long-running operations
- **Schema Validation:** Validate arguments before execution
- **Tabbed UI:** Separate tabs for Tools, Resources, and Prompts
- **Progress Indicator:** Visual feedback during operations

## Known Limitations

- No resource subscription support (notifications only)
- No streaming responses for large outputs
- No auto-reconnection (planned)

## Future Improvements

- [x] ~~Add configuration persistence (JSON settings file)~~
- [x] ~~Implement command history with up/down arrow navigation~~
- [x] ~~Add file-based logging for debugging~~
- [x] ~~Implement request timeouts~~
- [x] ~~Add MCP resources support~~
- [x] ~~Add MCP prompts support~~
- [x] ~~Add schema validation before tool execution~~
- [ ] Implement auto-reconnection on connection loss
- [ ] Add favorites/recent servers management UI
- [ ] Support streaming responses for large outputs
- [ ] Add resource subscription with live updates

## AI Assistant Guidelines

When working on this codebase:

1. **Read before modifying** - Always read existing files before making changes
2. **Follow patterns** - Match existing code style and architecture
3. **Async consistency** - Use async/await throughout, never block on tasks
4. **UI thread safety** - Always dispatch UI updates to the main thread
5. **Minimal changes** - Only modify what's necessary for the task
6. **Test manually** - Verify changes work in Revit before committing

### Common Tasks

**Adding a new MCP operation:**
1. Add method to `McpClient.cs`
2. Update UI in `McpDockablePane.xaml.cs` to expose it
3. Handle responses and errors appropriately

**Modifying the UI:**
1. Edit XAML for layout changes
2. Update code-behind for behavior
3. Maintain consistent styling with existing controls

**Debugging MCP communication:**
1. Check OutputText for error messages
2. Review `StdioTransport.ErrorReceived` events
3. Verify server process started correctly
