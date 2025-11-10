package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"time"

	"rendercv-go-backend/config"
)

// CVService handles interaction with the Uptal CV API
type CVService struct {
	BaseURL string
	Timeout int
}

// CVServiceError represents an error from the CV service
type CVServiceError struct {
	Message    string
	StatusCode int
}

func (e *CVServiceError) Error() string {
	return e.Message
}

// NewCVService creates a new CV service instance
func NewCVService(config *config.Config) *CVService {
	return &CVService{
		BaseURL: config.CVAPIBaseURL,
		Timeout: config.CVAPITimeout,
	}
}

// GetCVByCode fetches CV data from the API using cv_code
func (s *CVService) GetCVByCode(cvCode string) (map[string]interface{}, error) {
	client := &http.Client{
		Timeout: time.Duration(s.Timeout) * time.Second,
	}

	apiURL := fmt.Sprintf("%s/%s", s.BaseURL, cvCode)
	log.Printf("Fetching CV from: %s", apiURL)

	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to create request: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	resp, err := client.Do(req)
	if err != nil {
		if os.IsTimeout(err) {
			return nil, &CVServiceError{
				Message:    fmt.Sprintf("Request to CV API timed out after %ds", s.Timeout),
				StatusCode: http.StatusGatewayTimeout,
			}
		}
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to fetch CV: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("CV not found: %s", cvCode),
			StatusCode: http.StatusNotFound,
		}
	}

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("API returned status code %d: %s", resp.StatusCode, string(body)),
			StatusCode: resp.StatusCode,
		}
	}

	var cvData map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&cvData); err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Invalid response format from CV API: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	log.Printf("Successfully fetched CV data for code: %s", cvCode)
	return cvData, nil
}

// UpdateCVEdits updates CV with new file via the API
func (s *CVService) UpdateCVEdits(cvCode string, file multipart.File) (map[string]interface{}, error) {
	client := &http.Client{
		Timeout: time.Duration(s.Timeout*3) * time.Second, // Longer timeout for file upload and processing
	}

	apiURL := fmt.Sprintf("%s/%s/edits", s.BaseURL, cvCode)
	log.Printf("Updating CV at: %s", apiURL)

	// Create a new multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Add the file to the form
	part, err := writer.CreateFormFile("cv", "cv.pdf")
	if err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to create form file: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	_, err = io.Copy(part, file)
	if err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to copy file data: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	err = writer.Close()
	if err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to close form writer: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	req, err := http.NewRequest("POST", apiURL, body)
	if err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to create request: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := client.Do(req)
	if err != nil {
		if os.IsTimeout(err) {
			return nil, &CVServiceError{
				Message:    fmt.Sprintf("Request to CV API timed out after %ds", s.Timeout*3),
				StatusCode: http.StatusGatewayTimeout,
			}
		}
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Failed to update CV: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("CV not found: %s", cvCode),
			StatusCode: http.StatusNotFound,
		}
	}

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("API returned status code %d: %s", resp.StatusCode, string(body)),
			StatusCode: resp.StatusCode,
		}
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, &CVServiceError{
			Message:    fmt.Sprintf("Invalid response format from CV API: %v", err),
			StatusCode: http.StatusInternalServerError,
		}
	}

	log.Printf("Successfully updated CV for code: %s", cvCode)
	return result, nil
}

