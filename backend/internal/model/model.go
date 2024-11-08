package model

import "gorm.io/gorm"

type Guild struct {
	gorm.Model
	GuildID     string `gorm:"uniqueIndex"`
	Prefix      string `gorm:"default:'!'"`
	MusicVolume int    `gorm:"default:100"`
}

type DeletedMessage struct {
	gorm.Model
	GuildID   string
	ChannelID string
	MessageID string
	Content   string
	AuthorID  string
}

type EditedMessage struct {
	gorm.Model
	GuildID    string
	ChannelID  string
	MessageID  string
	OldContent string
	NewContent string
	AuthorID   string
}
