using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace BAC_MCP.Core
{
    public class ServerProfile
    {
        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("commandType")]
        public int CommandType { get; set; } = 0; // 0=npx, 1=node, 2=python, 3=custom

        [JsonProperty("command")]
        public string Command { get; set; } = "";

        [JsonProperty("arguments")]
        public string Arguments { get; set; } = "";

        [JsonProperty("environmentVariables")]
        public Dictionary<string, string> EnvironmentVariables { get; set; } = new();

        [JsonProperty("lastUsed")]
        public DateTime LastUsed { get; set; } = DateTime.Now;

        [JsonProperty("isFavorite")]
        public bool IsFavorite { get; set; } = false;

        [JsonProperty("useCount")]
        public int UseCount { get; set; } = 0;

        public ServerProfile Clone()
        {
            return new ServerProfile
            {
                Name = Name,
                CommandType = CommandType,
                Command = Command,
                Arguments = Arguments,
                EnvironmentVariables = new Dictionary<string, string>(EnvironmentVariables),
                LastUsed = LastUsed,
                IsFavorite = IsFavorite,
                UseCount = UseCount
            };
        }

        public override string ToString() => Name;

        public override bool Equals(object? obj)
        {
            if (obj is not ServerProfile other) return false;
            return Name == other.Name &&
                   Command == other.Command &&
                   Arguments == other.Arguments;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(Name, Command, Arguments);
        }
    }
}
