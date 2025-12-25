using System.Collections.Generic;
using Newtonsoft.Json;

namespace BAC_MCP.Mcp
{
    public class McpTool
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("inputSchema")]
        public McpToolInputSchema? InputSchema { get; set; }

        public string GetArgumentsTemplate()
        {
            if (InputSchema?.Properties == null || InputSchema.Properties.Count == 0)
                return "{}";

            var template = new Dictionary<string, object>();
            foreach (var prop in InputSchema.Properties)
            {
                var propType = prop.Value.Type?.ToLower() ?? "string";
                template[prop.Key] = propType switch
                {
                    "string" => "",
                    "number" => 0,
                    "integer" => 0,
                    "boolean" => false,
                    "array" => new object[] { },
                    "object" => new Dictionary<string, object>(),
                    _ => ""
                };
            }

            return JsonConvert.SerializeObject(template, Formatting.Indented);
        }
    }

    public class McpToolInputSchema
    {
        [JsonProperty("type")]
        public string Type { get; set; } = "object";

        [JsonProperty("properties")]
        public Dictionary<string, McpToolProperty>? Properties { get; set; }

        [JsonProperty("required")]
        public List<string>? Required { get; set; }
    }

    public class McpToolProperty
    {
        [JsonProperty("type")]
        public string? Type { get; set; }

        [JsonProperty("description")]
        public string? Description { get; set; }

        [JsonProperty("enum")]
        public List<string>? Enum { get; set; }
    }
}
