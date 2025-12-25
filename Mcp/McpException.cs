using System;
using Newtonsoft.Json.Linq;

namespace BAC_MCP.Mcp
{
    public class McpException : Exception
    {
        public int? ErrorCode { get; }
        public JToken? ErrorData { get; }

        public McpException(string message, int? code = null, JToken? data = null)
            : base(FormatMessage(message, code))
        {
            ErrorCode = code;
            ErrorData = data;
        }

        private static string FormatMessage(string message, int? code)
        {
            if (code == null) return message;

            string prefix = code switch
            {
                -32700 => "Parse Error",
                -32600 => "Invalid Request",
                -32601 => "Method Not Found",
                -32602 => "Invalid Parameters",
                -32603 => "Internal Error",
                _ => $"Error {code}"
            };

            return $"{prefix}: {message}";
        }

        public string GetUserFriendlyMessage()
        {
            return ErrorCode switch
            {
                -32700 => "The server couldn't parse the request. This might be a bug.",
                -32600 => "The request format was invalid.",
                -32601 => "The requested operation is not supported by this server.",
                -32602 => $"Invalid parameters: {Message}",
                -32603 => $"Server internal error: {Message}",
                _ => Message
            };
        }

        public bool IsRetryable()
        {
            return ErrorCode switch
            {
                -32603 => true,  // Internal error might be transient
                _ => false
            };
        }
    }
}
