package handler

import (
	"backend/internal/model"
	"net/http"

	"github.com/gin-gonic/gin"
)

func (h *Handler) StoreDeletedMessage(c *gin.Context) {
	var msg model.DeletedMessage
	if err := c.ShouldBindJSON(&msg); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.db.Create(&msg); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, msg)
}

func (h *Handler) GetRecentDeletedMessages(c *gin.Context) {
	guildID := c.Param("guildID")
	limit := 10 // Could make this configurable

	var messages []model.DeletedMessage
	err := h.db.Where("guild_id = ?", guildID).
		Order("created_at desc").
		Limit(limit).
		Find(&messages)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error})
		return
	}

	c.JSON(http.StatusOK, messages)
}

func (h *Handler) StoreEditedMessage(c *gin.Context) {
	var msg model.EditedMessage
	if err := c.ShouldBindJSON(&msg); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.db.Create(&msg); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, msg)
}

func (h *Handler) GetRecentEditedMessages(c *gin.Context) {
	guildID := c.Param("guildID")
	limit := 10 // Could make this configurable

	var messages []model.EditedMessage
	err := h.db.Where("guild_id = ?", guildID).
		Order("created_at desc").
		Limit(limit).
		Find(&messages)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error})
		return
	}

	c.JSON(http.StatusOK, messages)
}
