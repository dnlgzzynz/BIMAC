using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;

namespace BAC_MCP.Core
{
    public class Settings
    {
        private static readonly string SettingsDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "BAC_MCP");

        private static readonly string SettingsPath = Path.Combine(SettingsDirectory, "settings.json");

        private static Settings? _instance;
        private static readonly object _lock = new();

        // Last used server configuration
        [JsonProperty("lastServerIndex")]
        public int LastServerIndex { get; set; } = 0;

        [JsonProperty("lastCustomServer")]
        public ServerProfile? LastCustomServer { get; set; }

        // Server management
        [JsonProperty("favoriteServers")]
        public List<ServerProfile> FavoriteServers { get; set; } = new();

        [JsonProperty("recentServers")]
        public List<ServerProfile> RecentServers { get; set; } = new();

        [JsonProperty("maxRecentServers")]
        public int MaxRecentServers { get; set; } = 10;

        // Command history
        [JsonProperty("commandHistory")]
        public List<string> CommandHistory { get; set; } = new();

        [JsonProperty("maxHistoryItems")]
        public int MaxHistoryItems { get; set; } = 50;

        // Connection settings
        [JsonProperty("defaultTimeoutMs")]
        public int DefaultTimeoutMs { get; set; } = 30000;

        [JsonProperty("autoReconnect")]
        public bool AutoReconnect { get; set; } = false;

        [JsonProperty("reconnectDelayMs")]
        public int ReconnectDelayMs { get; set; } = 5000;

        // UI preferences
        [JsonProperty("showToolDescriptions")]
        public bool ShowToolDescriptions { get; set; } = true;

        [JsonProperty("autoExpandCustomPanel")]
        public bool AutoExpandCustomPanel { get; set; } = false;

        public static Settings Instance
        {
            get
            {
                if (_instance == null)
                {
                    lock (_lock)
                    {
                        _instance ??= Load();
                    }
                }
                return _instance;
            }
        }

        public static Settings Load()
        {
            try
            {
                if (File.Exists(SettingsPath))
                {
                    string json = File.ReadAllText(SettingsPath);
                    var settings = JsonConvert.DeserializeObject<Settings>(json);
                    if (settings != null)
                    {
                        Logger.Info("Settings loaded successfully");
                        return settings;
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to load settings", ex);
            }

            Logger.Info("Using default settings");
            return new Settings();
        }

        public void Save()
        {
            try
            {
                Directory.CreateDirectory(SettingsDirectory);

                string json = JsonConvert.SerializeObject(this, Formatting.Indented);
                File.WriteAllText(SettingsPath, json);

                Logger.Debug("Settings saved");
            }
            catch (Exception ex)
            {
                Logger.Error("Failed to save settings", ex);
            }
        }

        public void AddToCommandHistory(string command)
        {
            if (string.IsNullOrWhiteSpace(command)) return;

            // Remove if already exists (to move to end)
            CommandHistory.Remove(command);

            // Add to end
            CommandHistory.Add(command);

            // Trim if over limit
            while (CommandHistory.Count > MaxHistoryItems)
            {
                CommandHistory.RemoveAt(0);
            }

            Save();
        }

        public void AddToRecentServers(ServerProfile server)
        {
            if (server == null) return;

            // Update the profile
            server.LastUsed = DateTime.Now;
            server.UseCount++;

            // Remove existing entry with same signature
            RecentServers.RemoveAll(s =>
                s.Command == server.Command && s.Arguments == server.Arguments);

            // Add to beginning
            RecentServers.Insert(0, server.Clone());

            // Trim if over limit
            while (RecentServers.Count > MaxRecentServers)
            {
                RecentServers.RemoveAt(RecentServers.Count - 1);
            }

            Save();
        }

        public void ToggleFavorite(ServerProfile server)
        {
            var existing = FavoriteServers.FirstOrDefault(s =>
                s.Command == server.Command && s.Arguments == server.Arguments);

            if (existing != null)
            {
                FavoriteServers.Remove(existing);
                server.IsFavorite = false;
            }
            else
            {
                server.IsFavorite = true;
                FavoriteServers.Add(server.Clone());
            }

            Save();
        }

        public bool IsFavorite(ServerProfile server)
        {
            return FavoriteServers.Any(s =>
                s.Command == server.Command && s.Arguments == server.Arguments);
        }

        public List<ServerProfile> GetAllServers()
        {
            // Combine favorites and recent, favorites first
            var all = new List<ServerProfile>();

            foreach (var fav in FavoriteServers.OrderByDescending(s => s.LastUsed))
            {
                fav.IsFavorite = true;
                all.Add(fav);
            }

            foreach (var recent in RecentServers.Where(r =>
                !FavoriteServers.Any(f => f.Command == r.Command && f.Arguments == r.Arguments)))
            {
                recent.IsFavorite = false;
                all.Add(recent);
            }

            return all;
        }

        public static string GetSettingsDirectory() => SettingsDirectory;
    }
}
