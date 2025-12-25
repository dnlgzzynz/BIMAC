using System;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace BAC_MCP.Commands
{
    [Transaction(TransactionMode.Manual)]
    public class OpenAssistantCommand : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            DockablePaneId dpid = new DockablePaneId(new Guid("B2A3C4D5-E6F7-4890-1234-567890ABCDEF"));
            DockablePane pane = commandData.Application.GetDockablePane(dpid);
            pane.Show();
            return Result.Succeeded;
        }
    }
}
