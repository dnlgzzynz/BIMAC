using System;
using System.Reflection;
using System.Windows.Media.Imaging;
using Autodesk.Revit.UI;
using Autodesk.Revit.Attributes;
using BAC_MCP.UI;

namespace BAC_MCP
{
    [Transaction(TransactionMode.Manual)]
    public class App : IExternalApplication
    {
        public static string ExecutingAssemblyPath = Assembly.GetExecutingAssembly().Location;

        public Result OnStartup(UIControlledApplication application)
        {
            // 1. Create Ribbon Tab
            string tabName = "BAC MCP";
            try
            {
                application.CreateRibbonTab(tabName);
            }
            catch (Exception)
            {
                // Tab might already exist
            }

            // 2. Create Ribbon Panel
            RibbonPanel panel = application.CreateRibbonPanel(tabName, "Main");

            // 3. Create Button
            string path = Assembly.GetExecutingAssembly().Location;
            PushButtonData buttonData = new PushButtonData("cmdOpenMcp", "Open\nAssistant", path, "BAC_MCP.Commands.OpenAssistantCommand");
            PushButton button = panel.AddItem(buttonData) as PushButton;
            button.ToolTip = "Open the BAC MCP Assistant";

            // 4. Register Dockable Pane
            McpDockablePane pane = new McpDockablePane();
            DockablePaneId dpid = new DockablePaneId(new Guid("B2A3C4D5-E6F7-4890-1234-567890ABCDEF"));
            application.RegisterDockablePane(dpid, "BAC MCP Assistant", pane as IDockablePaneProvider);

            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            return Result.Succeeded;
        }
    }
}
