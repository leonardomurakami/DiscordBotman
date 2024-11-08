package handler

import (
	"backend/internal/model"
	"net/http"

	"gorm.io/gorm"

	"github.com/gin-gonic/gin"
)

func (h *Handler) GetGuildPrefix(c *gin.Context) {
	guildID := c.Param("guildID")

	var guild model.Guild
	err := h.db.Where("guild_id = ?", guildID).First(&guild).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusOK, gin.H{"prefix": "!"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"prefix": guild.Prefix})
}

func (h *Handler) UpdateGuildPrefix(c *gin.Context) {
	guildID := c.Param("guildID")

	var body struct {
		Prefix string `json:"prefix" binding:"required"`
	}

	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var guild model.Guild
	if err := h.db.FirstOrCreate(&guild, model.Guild{GuildID: guildID}); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	guild.Prefix = body.Prefix
	if err := h.db.Save(&guild); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, guild)
}
