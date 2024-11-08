package server

import (
	"backend/internal/api/handler"
	"backend/internal/api/router"
	"backend/internal/config"
	"backend/internal/database"
	"fmt"
)

type Server struct {
	cfg *config.Config
}

func New(cfg *config.Config) *Server {
	return &Server{cfg: cfg}
}

func (s *Server) Start() error {
	db, err := database.New(s.cfg)
	if err != nil {
		return fmt.Errorf("failed to initialize database: %w", err)
	}

	h := handler.New(db)
	r := router.Setup(h)

	return r.Run(":" + s.cfg.Server.Port)
}
