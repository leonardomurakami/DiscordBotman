package handler

import "backend/internal/database"

type Handler struct {
	db *database.Database
}

func New(db *database.Database) *Handler {
	return &Handler{db: db}
}
