package router

import (
	"backend/internal/api/handler"

	"github.com/gin-gonic/gin"
)

func Setup(h *handler.Handler) *gin.Engine {
	r := gin.Default()

	// Guild routes
	r.GET("/guilds/:guildID/prefix", h.GetGuildPrefix)
	r.PUT("/guilds/:guildID/prefix", h.UpdateGuildPrefix)

	// Message routes
	r.POST("/messages/deleted", h.StoreDeletedMessage)
	r.GET("/guilds/:guildID/messages/deleted", h.GetRecentDeletedMessages)
	r.POST("/messages/edited", h.StoreEditedMessage)
	r.GET("/guilds/:guildID/messages/edited", h.GetRecentEditedMessages)

	return r
}
