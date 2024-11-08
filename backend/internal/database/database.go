// internal/database/database.go
package database

import (
	"backend/internal/config"
	"backend/internal/model"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Database struct {
	db *gorm.DB
}

func New(cfg *config.Config) (*Database, error) {
	db, err := gorm.Open(postgres.Open(cfg.Database.DSN), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	if err := db.AutoMigrate(&model.Guild{}, &model.DeletedMessage{}, &model.EditedMessage{}); err != nil {
		return nil, err
	}

	return &Database{db: db}, nil
}

// Create inserts a new record into the database
func (d *Database) Create(value interface{}) error {
	return d.db.Create(value).Error
}

// Save updates a record in the database
func (d *Database) Save(value interface{}) error {
	return d.db.Save(value).Error
}

// First finds the first record matching the given conditions
func (d *Database) First(dest interface{}, conds ...interface{}) error {
	return d.db.First(dest, conds...).Error
}

// Find finds records matching the given conditions
func (d *Database) Find(dest interface{}, conds ...interface{}) error {
	return d.db.Find(dest, conds...).Error
}

// Where adds a where clause to the query
func (d *Database) Where(query interface{}, args ...interface{}) *gorm.DB {
	return d.db.Where(query, args...)
}

// Order adds an order clause to the query
func (d *Database) Order(value interface{}) *gorm.DB {
	return d.db.Order(value)
}

// Limit adds a limit clause to the query
func (d *Database) Limit(limit int) *gorm.DB {
	return d.db.Limit(limit)
}

// FirstOrCreate gets first matched record or creates a new one
func (d *Database) FirstOrCreate(dest interface{}, conds ...interface{}) error {
	return d.db.FirstOrCreate(dest, conds...).Error
}

// Transaction starts a new transaction
func (d *Database) Transaction(fc func(tx *gorm.DB) error) error {
	return d.db.Transaction(fc)
}
