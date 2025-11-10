package handlers

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"

	"rendercv-go-backend/services"
)

// Handler struct holds the services and configuration needed by the handlers
type Handler struct {
	CVService *services.CVService
	PDFDir    string
}

// HealthCheck returns the health status of the service
func (h *Handler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"service": "rendercv-go-backend",
	})
}

// GetThemes returns available themes
func (h *Handler) GetThemes(c *gin.Context) {
	themes := []map[string]string{
		{"id": "classic", "name": "Classic"},
		{"id": "sb2nov", "name": "Sb2nov"},
		{"id": "moderncv", "name": "ModernCV"},
		{"id": "engineeringresumes", "name": "Engineering Resumes"},
		{"id": "engineeringclassic", "name": "Engineering Classic"},
	}
	c.JSON(http.StatusOK, themes)
}

// RenderCV generates PDF from CV data
func (h *Handler) RenderCV(c *gin.Context) {
	var cvData map[string]interface{}
	if err := c.ShouldBindJSON(&cvData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CV data provided"})
		return
	}

	// Log the incoming data for debugging
	log.Printf("Received CV data: %+v", cvData)

	// Generate unique filename
	pdfID := fmt.Sprintf("%s_%s", 
		generateRandomString(8), 
		time.Now().Format("20060102_150405"))
	pdfPath := filepath.Join(h.PDFDir, fmt.Sprintf("%s.pdf", pdfID))

	// Generate PDF using Python rendercv via shell script
	if err := services.GeneratePDF(cvData, pdfPath); err != nil {
		log.Printf("Error generating PDF: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Clean up old PDFs (keep only last 20)
	h.cleanupOldPDFs()

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"pdf_id":  pdfID,
		"pdf_url": fmt.Sprintf("/api/pdf/%s", pdfID),
	})
}

// GetPDF serves generated PDF
func (h *Handler) GetPDF(c *gin.Context) {
	pdfID := c.Param("pdf_id")
	pdfPath := filepath.Join(h.PDFDir, fmt.Sprintf("%s.pdf", pdfID))

	if _, err := os.Stat(pdfPath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "PDF not found"})
		return
	}

	c.Header("Content-Type", "application/pdf")
	c.Header("Access-Control-Allow-Origin", "http://localhost:5173")
	c.Header("Access-Control-Allow-Methods", "GET")
	c.Header("Access-Control-Allow-Headers", "Content-Type")

	c.File(pdfPath)
}

// ValidateCV validates CV data structure
func (h *Handler) ValidateCV(c *gin.Context) {
	var cvData map[string]interface{}
	if err := c.ShouldBindJSON(&cvData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CV data provided"})
		return
	}

	// Validate using Python rendercv via shell script
	valid, err := services.ValidateCV(cvData)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"valid":  false,
			"errors": []string{err.Error()},
		})
		return
	}

	if !valid {
		c.JSON(http.StatusBadRequest, gin.H{
			"valid":  false,
			"errors": []string{"Invalid CV data structure"},
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"valid":   true,
		"message": "CV data is valid",
	})
}

// GetSampleCV gets CV data from Uptal API using cv_code
func (h *Handler) GetSampleCV(c *gin.Context) {
	cvCode := c.Param("cv_code")

	cvData, err := h.CVService.GetCVByCode(cvCode)
	if err != nil {
		log.Printf("CV Service error: %v", err)
		c.JSON(err.StatusCode, gin.H{"error": err.Message})
		return
	}

	response, ok := cvData["data"].(map[string]interface{})
	if !ok {
		c.JSON(http.StatusNotFound, gin.H{"error": "CV not found"})
		return
	}

	if response == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "CV not found"})
		return
	}

	// Check if enhancement_result is not empty
	if enhancementResult, exists := response["enhancement_result"]; exists && enhancementResult != nil {
		if positionMatch, exists := response["position_match"]; exists && positionMatch != nil {
			if enhancementMap, ok := enhancementResult.(map[string]interface{}); ok {
				enhancementMap["position_match"] = positionMatch
			}
		}
		c.JSON(http.StatusOK, enhancementResult)
		return
	} else {
		c.JSON(http.StatusBadRequest, gin.H{"error": "CV not enhanced"})
		return
	}
}

// ExportCV exports CV in different formats
func (h *Handler) ExportCV(c *gin.Context) {
	format := c.Param("format")
	var cvData map[string]interface{}
	if err := c.ShouldBindJSON(&cvData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CV data provided"})
		return
	}

	switch strings.ToLower(format) {
	case "yaml":
		yamlContent, err := services.ExportAsYAML(cvData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.Header("Content-Type", "text/yaml")
		c.Header("Content-Disposition", "attachment; filename=cv.yaml")
		c.String(http.StatusOK, yamlContent)
	case "json":
		c.JSON(http.StatusOK, cvData)
	case "markdown":
		markdownContent, err := services.ExportAsMarkdown(cvData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.Header("Content-Type", "text/markdown")
		c.Header("Content-Disposition", "attachment; filename=cv.md")
		c.String(http.StatusOK, markdownContent)
	default:
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported format"})
	}
}

// Helper function to clean up old PDFs (keep only last 20)
func (h *Handler) cleanupOldPDFs() {
	files, err := os.ReadDir(h.PDFDir)
	if err != nil {
		log.Printf("Error reading PDF directory: %v", err)
		return
	}

	var pdfFiles []os.FileInfo
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".pdf") {
			info, _ := file.Info()
			pdfFiles = append(pdfFiles, info)
		}
	}

	// Sort by modification time (newest first)
	for i := 0; i < len(pdfFiles)-1; i++ {
		for j := i + 1; j < len(pdfFiles); j++ {
			if pdfFiles[i].ModTime().Before(pdfFiles[j].ModTime()) {
				pdfFiles[i], pdfFiles[j] = pdfFiles[j], pdfFiles[i]
			}
		}
	}

	// Remove old PDFs, keeping only the 20 most recent
	for i := 20; i < len(pdfFiles); i++ {
		os.Remove(filepath.Join(h.PDFDir, pdfFiles[i].Name()))
	}
}

// Helper function to generate random string for PDF ID
func generateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[time.Now().UnixNano()%int64(len(charset))]
	}
	return string(b)
}