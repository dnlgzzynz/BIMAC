using System.Collections.Generic;
using Newtonsoft.Json;

namespace BAC_MCP.Mcp
{
    public class McpPrompt
    {
        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string? Description { get; set; }

        [JsonProperty("arguments")]
        public List<McpPromptArgument>? Arguments { get; set; }

        public override string ToString() => Name;

        public string GetArgumentsTemplate()
        {
            if (Arguments == null || Arguments.Count == 0)
                return "{}";

            var template = new Dictionary<string, object>();
            foreach (var arg in Arguments)
            {
                template[arg.Name] = arg.Required ? "<required>" : "";
            }

            return JsonConvert.SerializeObject(template, Formatting.Indented);
        }
    }

    public class McpPromptArgument
    {
        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string? Description { get; set; }

        [JsonProperty("required")]
        public bool Required { get; set; }
    }

    public class McpPromptMessage
    {
        [JsonProperty("role")]
        public string Role { get; set; } = "user";

        [JsonProperty("content")]
        public McpPromptContent Content { get; set; } = new();
    }

    public class McpPromptContent
    {
        [JsonProperty("type")]
        public string Type { get; set; } = "text";

        [JsonProperty("text")]
        public string? Text { get; set; }

        [JsonProperty("resource")]
        public McpEmbeddedResource? Resource { get; set; }
    }

    public class McpEmbeddedResource
    {
        [JsonProperty("uri")]
        public string Uri { get; set; } = "";

        [JsonProperty("mimeType")]
        public string? MimeType { get; set; }

        [JsonProperty("text")]
        public string? Text { get; set; }

        [JsonProperty("blob")]
        public string? Blob { get; set; }
    }
}
