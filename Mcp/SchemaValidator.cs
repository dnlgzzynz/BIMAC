using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace BAC_MCP.Mcp
{
    public class ValidationResult
    {
        public bool IsValid { get; set; } = true;
        public List<string> Errors { get; set; } = new();
        public List<string> Warnings { get; set; } = new();

        public string GetErrorSummary()
        {
            if (IsValid) return string.Empty;
            return string.Join("\n", Errors);
        }
    }

    public static class SchemaValidator
    {
        public static ValidationResult Validate(JObject arguments, McpToolInputSchema? schema)
        {
            var result = new ValidationResult();

            if (schema == null)
            {
                return result; // No schema = no validation needed
            }

            // Check required properties
            if (schema.Required != null)
            {
                foreach (var required in schema.Required)
                {
                    if (!arguments.ContainsKey(required))
                    {
                        result.IsValid = false;
                        result.Errors.Add($"Missing required property: '{required}'");
                    }
                    else if (arguments[required]?.Type == JTokenType.Null)
                    {
                        result.IsValid = false;
                        result.Errors.Add($"Required property '{required}' cannot be null");
                    }
                    else if (arguments[required]?.Type == JTokenType.String &&
                             string.IsNullOrEmpty(arguments[required]?.Value<string>()))
                    {
                        result.Warnings.Add($"Property '{required}' is empty");
                    }
                }
            }

            // Validate property types
            if (schema.Properties != null)
            {
                foreach (var prop in arguments.Properties())
                {
                    if (schema.Properties.TryGetValue(prop.Name, out var propSchema))
                    {
                        ValidateProperty(prop.Name, prop.Value, propSchema, result);
                    }
                    else
                    {
                        // Unknown property - just warn
                        result.Warnings.Add($"Unknown property: '{prop.Name}'");
                    }
                }
            }

            return result;
        }

        private static void ValidateProperty(string name, JToken value, McpToolProperty schema, ValidationResult result)
        {
            // Skip null values (already checked in required)
            if (value.Type == JTokenType.Null) return;

            // Type validation
            if (!string.IsNullOrEmpty(schema.Type))
            {
                bool typeValid = IsValidType(value, schema.Type);
                if (!typeValid)
                {
                    result.IsValid = false;
                    result.Errors.Add($"Property '{name}' should be of type '{schema.Type}', got '{GetTypeName(value)}'");
                    return; // Skip further validation for this property
                }
            }

            // Enum validation
            if (schema.Enum != null && schema.Enum.Count > 0)
            {
                string stringValue = value.Type == JTokenType.String
                    ? value.Value<string>() ?? ""
                    : value.ToString();

                if (!schema.Enum.Contains(stringValue))
                {
                    result.IsValid = false;
                    result.Errors.Add(
                        $"Property '{name}' must be one of: [{string.Join(", ", schema.Enum)}], got '{stringValue}'");
                }
            }
        }

        private static bool IsValidType(JToken value, string expectedType)
        {
            return expectedType.ToLower() switch
            {
                "string" => value.Type == JTokenType.String,
                "number" => value.Type == JTokenType.Float || value.Type == JTokenType.Integer,
                "integer" => value.Type == JTokenType.Integer,
                "boolean" => value.Type == JTokenType.Boolean,
                "array" => value.Type == JTokenType.Array,
                "object" => value.Type == JTokenType.Object,
                "null" => value.Type == JTokenType.Null,
                _ => true // Unknown types pass validation
            };
        }

        private static string GetTypeName(JToken value)
        {
            return value.Type switch
            {
                JTokenType.String => "string",
                JTokenType.Integer => "integer",
                JTokenType.Float => "number",
                JTokenType.Boolean => "boolean",
                JTokenType.Array => "array",
                JTokenType.Object => "object",
                JTokenType.Null => "null",
                _ => value.Type.ToString().ToLower()
            };
        }

        public static JObject CreateDefaultArguments(McpToolInputSchema? schema)
        {
            var args = new JObject();

            if (schema?.Properties == null) return args;

            foreach (var prop in schema.Properties)
            {
                bool isRequired = schema.Required?.Contains(prop.Key) ?? false;

                // Only add required properties with default values
                if (isRequired)
                {
                    args[prop.Key] = GetDefaultValue(prop.Value);
                }
            }

            return args;
        }

        private static JToken GetDefaultValue(McpToolProperty prop)
        {
            // If there's an enum, use first value
            if (prop.Enum != null && prop.Enum.Count > 0)
            {
                return prop.Enum[0];
            }

            return prop.Type?.ToLower() switch
            {
                "string" => "",
                "number" => 0,
                "integer" => 0,
                "boolean" => false,
                "array" => new JArray(),
                "object" => new JObject(),
                _ => ""
            };
        }
    }
}
