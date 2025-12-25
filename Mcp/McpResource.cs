using System.Collections.Generic;
using Newtonsoft.Json;

namespace BAC_MCP.Mcp
{
    public class McpResource
    {
        [JsonProperty("uri")]
        public string Uri { get; set; } = "";

        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string? Description { get; set; }

        [JsonProperty("mimeType")]
        public string? MimeType { get; set; }

        public override string ToString() => Name;
    }

    public class McpResourceContent
    {
        [JsonProperty("uri")]
        public string Uri { get; set; } = "";

        [JsonProperty("mimeType")]
        public string? MimeType { get; set; }

        [JsonProperty("text")]
        public string? Text { get; set; }

        [JsonProperty("blob")]
        public string? Blob { get; set; } // Base64 encoded binary data

        public bool IsText => !string.IsNullOrEmpty(Text);
        public bool IsBinary => !string.IsNullOrEmpty(Blob);

        public string GetDisplayContent(int maxLength = 5000)
        {
            if (IsText)
            {
                if (Text!.Length <= maxLength)
                    return Text;
                return Text.Substring(0, maxLength) + $"\n... (truncated, {Text.Length - maxLength} more characters)";
            }

            if (IsBinary)
            {
                return $"[Binary content: {Blob!.Length} bytes, type: {MimeType ?? "unknown"}]";
            }

            return "[No content]";
        }
    }

    public class McpResourceTemplate
    {
        [JsonProperty("uriTemplate")]
        public string UriTemplate { get; set; } = "";

        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string? Description { get; set; }

        [JsonProperty("mimeType")]
        public string? MimeType { get; set; }
    }
}
