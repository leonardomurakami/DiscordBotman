package config

import "os"

type Config struct {
	Database DatabaseConfig
	Server   ServerConfig
}

type DatabaseConfig struct {
	DSN string
}

type ServerConfig struct {
	Port string
}

func Load() (*Config, error) {
	return &Config{
		Database: DatabaseConfig{
			DSN: getEnv("DATABASE_URL", "host=localhost user=postgres password=postgres dbname=discordbot port=5432 sslmode=disable"),
		},
		Server: ServerConfig{
			Port: getEnv("PORT", "8080"),
		},
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
