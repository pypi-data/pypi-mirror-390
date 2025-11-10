package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"rendercv-go-backend/config"
	"rendercv-go-backend/handlers"
	"rendercv-go-backend/services"
)

func main() {
	// Load environment variables from .env file
	if err := godotenv.Load(); err != nil {
		log.Printf("No .env file found: %v", err)
	}

	// Initialize configuration
	cfg := &config.Config{
		CVAPIBaseURL: os.Getenv("CV_API_BASE_URL"),
		CVAPITimeout: getEnvAsInt("CV_API_TIMEOUT", 10),
		OpenAIAPIKey: os.Getenv("OPENAI_API_KEY"),
	}

	// Set default CV API base URL if not provided
	if cfg.CVAPIBaseURL == "" {
		cfg.CVAPIBaseURL = "https://api-v2.uptal.com/cv-enhance"
	}

	// Initialize services
	cvService := services.NewCVService(cfg)

	// Create temporary directory for PDFs if it doesn't exist
	pdfDir := "generated_pdfs"
	if err := os.MkdirAll(pdfDir, 0755); err != nil {
		log.Fatalf("Failed to create PDF directory: %v", err)
	}

	// Clean up old PDFs on startup
	cleanupOldPDFs(pdfDir)

	// Set up Gin router
	router := gin.Default()

	// Configure CORS
	config := cors.DefaultConfig()
	config.AllowOrigins = []string{"http://localhost:3000", "http://localhost:5173"}
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Length", "Content-Type", "Authorization"}
	router.Use(cors.New(config))

	// Define handlers
	handler := &handlers.Handler{
		CVService: cvService,
		PDFDir:    pdfDir,
	}

	// Health check endpoint
	router.GET("/api/health", handler.HealthCheck)

	// Theme endpoint
	router.GET("/api/themes", handler.GetThemes)

	// Render endpoint
	router.POST("/api/render", handler.RenderCV)

	// PDF serving endpoint
	router.GET("/api/pdf/:pdf_id", handler.GetPDF)

	// Validation endpoint
	router.POST("/api/validate", handler.ValidateCV)

	// Sample CV endpoint
	router.GET("/api/sample/:cv_code", handler.GetSampleCV)

	// Export endpoint
	router.POST("/api/export/:format", handler.ExportCV)

	// Start the server
	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		var result int
		fmt.Sscanf(value, "%d", &result)
		return result
	}
	return defaultValue
}

func cleanupOldPDFs(pdfDir string) {
	// Clean up PDF files older than 1 hour
	now := time.Now()
	err := filepath.Walk(pdfDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && filepath.Ext(path) == ".pdf" {
			if now.Sub(info.ModTime()) > time.Hour {
				return os.Remove(path)
			}
		}
		return nil
	})
	if err != nil {
		log.Printf("Error cleaning up old PDFs: %v", err)
	}
}