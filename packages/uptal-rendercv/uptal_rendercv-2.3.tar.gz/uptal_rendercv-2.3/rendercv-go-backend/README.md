# RenderCV Go Backend

This is a Go-based backend implementation for the RenderCV service. It replicates the functionality of the original Python backend but uses Go as the primary language while still leveraging the Python `rendercv[full]` package via shell commands.

## Features

- Generate PDFs from CV data using Python's RenderCV package
- Validate CV data structures
- Export CVs in different formats (YAML, JSON, Markdown)
- Fetch CV data from Uptal API using CV code
- Serve generated PDFs
- Health check and theme endpoints
- CORS support for frontend integration

## Requirements

- Go 1.21 or higher
- Python 3.8 or higher
- pip package: `rendercv[full]`
- Typst for PDF generation

## Installation

1. Clone the repository
2. Install Go dependencies:
   ```
   go mod download
   ```
3. Install the Python rendercv package:
   ```
   pip install "rendercv[full]"
   ```
4. Install Typst for PDF generation (https://github.com/typst/typst)

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# CV API Configuration
CV_API_BASE_URL=https://api-v2.uptal.com/cv-enhance
CV_API_TIMEOUT=10
```

## Running the Application

1. Build the application:
   ```
   go build -o main ./cmd/server
   ```

2. Run the application:
   ```
   ./main
   ```

The server will start on port 5000 by default.

## Docker

To build and run with Docker:

```bash
# Build the image
docker build -t rendercv-go-backend .

# Run the container
docker run -p 5000:5000 -e CV_API_BASE_URL=https://api-v2.uptal.com/cv-enhance -e CV_API_TIMEOUT=10 -e OPENAI_API_KEY=your_key_here rendercv-go-backend
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/themes` - Get available themes
- `POST /api/render` - Generate PDF from CV data
- `GET /api/pdf/:pdf_id` - Serve generated PDF
- `POST /api/validate` - Validate CV data
- `GET /api/sample/:cv_code` - Get CV data by code
- `POST /api/export/:format` - Export CV in different formats (yaml, json, markdown)

## Architecture

- Uses Gin framework for routing and middleware
- Implements service layer for business logic
- Communicates with Python rendercv via shell command execution
- Stores generated PDFs in local filesystem
- Uses environment variables for configuration