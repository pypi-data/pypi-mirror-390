package services

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// GeneratePDF generates a PDF from CV data using Python rendercv via shell script
func GeneratePDF(cvData map[string]interface{}, outputPath string) error {
	// Create a temporary JSON file with the CV data
	tempDir := filepath.Dir(outputPath)
	tempJSONFile := filepath.Join(tempDir, "temp_cv_data.json")

	jsonData, err := json.Marshal(cvData)
	if err != nil {
		return fmt.Errorf("failed to marshal CV data to JSON: %v", err)
	}

	if err := os.WriteFile(tempJSONFile, jsonData, 0644); err != nil {
		return fmt.Errorf("failed to write temporary JSON file: %v", err)
	}
	defer os.Remove(tempJSONFile) // Clean up temp file

	// Prepare the Python script to call rendercv
	script := fmt.Sprintf(`
import json
import sys
from pathlib import Path

# Import rendercv functions
import rendercv.api.functions as rcv_api

# Read CV data from the temporary file
with open('%s', 'r') as f:
    cv_data = json.load(f)

# Extract the filename without extension for the output
output_path = Path('%s')
typst_path = output_path.with_suffix('.typ')

# Generate the Typst file first
errors = rcv_api.create_a_typst_file_from_a_python_dictionary(
    cv_data,
    typst_path
)

if not errors:
    # Then render the PDF from the Typst file
    import rendercv.renderer.renderer as renderer
    try:
        generated_pdf_path = renderer.render_a_pdf_from_typst(typst_path)
        # Move the PDF to our desired location if needed
        if generated_pdf_path != output_path:
            import shutil
            shutil.move(str(generated_pdf_path), str(output_path))
        # Clean up the Typst file
        typst_path.unlink(missing_ok=True)
    except Exception as e:
        errors = [{"error": str(e)}]
        print(f"Error rendering PDF: {e}", file=sys.stderr)
        sys.exit(1)

if errors:
    print(f"RenderCV validation errors: {errors}", file=sys.stderr)
    sys.exit(1)

print("PDF generated successfully")
`, tempJSONFile, outputPath)

	// Write the Python script to a temporary file
	scriptFile := filepath.Join(tempDir, "generate_pdf.py")
	if err := os.WriteFile(scriptFile, []byte(script), 0644); err != nil {
		return fmt.Errorf("failed to write temporary Python script: %v", err)
	}
	defer os.Remove(scriptFile) // Clean up script file

	// Execute the Python script
	cmd := exec.Command("python3", scriptFile)
	output, err := cmd.CombinedOutput()

	if err != nil {
		return fmt.Errorf("failed to execute Python script: %v, output: %s", err, string(output))
	}

	return nil
}

// ValidateCV validates CV data structure using Python rendercv via shell script
func ValidateCV(cvData map[string]interface{}) (bool, error) {
	// Create a temporary JSON file with the CV data
	tempDir := os.TempDir()
	tempJSONFile := filepath.Join(tempDir, "temp_validate_data.json")

	jsonData, err := json.Marshal(cvData)
	if err != nil {
		return false, fmt.Errorf("failed to marshal CV data to JSON: %v", err)
	}

	if err := os.WriteFile(tempJSONFile, jsonData, 0644); err != nil {
		return false, fmt.Errorf("failed to write temporary JSON file: %v", err)
	}
	defer os.Remove(tempJSONFile) // Clean up temp file

	// Prepare the Python script to validate CV data
	script := fmt.Sprintf(`
import json
import sys

# Import rendercv functions
import rendercv.api.functions as rcv_api

# Read CV data from the temporary file
with open('%s', 'r') as f:
    cv_data = json.load(f)

# Try to parse with RenderCV
try:
    data_model = rcv_api.read_a_python_dictionary_and_return_a_data_model(cv_data)
    
    if data_model is None:
        print("Invalid CV data structure", file=sys.stderr)
        sys.exit(1)
    
    print("Valid")
except Exception as e:
    print(f"Validation error: {e}", file=sys.stderr)
    sys.exit(1)
`, tempJSONFile)

	// Write the Python script to a temporary file
	scriptFile := filepath.Join(tempDir, "validate_cv.py")
	if err := os.WriteFile(scriptFile, []byte(script), 0644); err != nil {
		return false, fmt.Errorf("failed to write temporary Python script: %v", err)
	}
	defer os.Remove(scriptFile) // Clean up script file

	// Execute the Python script
	cmd := exec.Command("python3", scriptFile)
	output, err := cmd.CombinedOutput()

	if err != nil {
		// Check if the error is just about invalid data
		outputStr := string(output)
		if strings.Contains(outputStr, "Invalid CV data structure") {
			return false, nil
		}
		return false, fmt.Errorf("failed to execute Python validation script: %v, output: %s", err, outputStr)
	}

	// Check if the output indicates validity
	return strings.TrimSpace(string(output)) == "Valid\n", nil
}

// ExportAsYAML exports CV data as YAML format using Python rendercv via shell script
func ExportAsYAML(cvData map[string]interface{}) (string, error) {
	// Create a temporary JSON file with the CV data
	tempDir := os.TempDir()
	tempJSONFile := filepath.Join(tempDir, "temp_export_data.json")

	jsonData, err := json.Marshal(cvData)
	if err != nil {
		return "", fmt.Errorf("failed to marshal CV data to JSON: %v", err)
	}

	if err := os.WriteFile(tempJSONFile, jsonData, 0644); err != nil {
		return "", fmt.Errorf("failed to write temporary JSON file: %v", err)
	}
	defer os.Remove(tempJSONFile) // Clean up temp file

	// Create a temporary file for the output YAML
	tempYAMLFile := filepath.Join(tempDir, "export_output.yaml")

	// Prepare the Python script to export as YAML
	script := fmt.Sprintf(`
import json
import sys
from pathlib import Path

# Import rendercv functions
import rendercv.api.functions as rcv_api

# Read CV data from the temporary file
with open('%s', 'r') as f:
    cv_data = json.load(f)

# Create YAML file
errors = rcv_api.create_a_yaml_file_from_a_python_dictionary(
    cv_data,
    Path('%s')
)

if errors:
    print(f"RenderCV export errors: {errors}", file=sys.stderr)
    sys.exit(1)

print("YAML export successful")
`, tempJSONFile, tempYAMLFile)

	// Write the Python script to a temporary file
	scriptFile := filepath.Join(tempDir, "export_yaml.py")
	if err := os.WriteFile(scriptFile, []byte(script), 0644); err != nil {
		return "", fmt.Errorf("failed to write temporary Python script: %v", err)
	}
	defer os.Remove(scriptFile) // Clean up script file

	// Execute the Python script
	cmd := exec.Command("python3", scriptFile)
	output, err := cmd.CombinedOutput()

	if err != nil {
		return "", fmt.Errorf("failed to execute Python export script: %v, output: %s", err, string(output))
	}

	// Read the generated YAML file
	yamlContent, err := os.ReadFile(tempYAMLFile)
	if err != nil {
		return "", fmt.Errorf("failed to read generated YAML file: %v", err)
	}
	defer os.Remove(tempYAMLFile) // Clean up temp YAML file

	return string(yamlContent), nil
}

// ExportAsMarkdown exports CV data as Markdown format using Python rendercv via shell script
func ExportAsMarkdown(cvData map[string]interface{}) (string, error) {
	// Create a temporary JSON file with the CV data
	tempDir := os.TempDir()
	tempJSONFile := filepath.Join(tempDir, "temp_export_md_data.json")

	jsonData, err := json.Marshal(cvData)
	if err != nil {
		return "", fmt.Errorf("failed to marshal CV data to JSON: %v", err)
	}

	if err := os.WriteFile(tempJSONFile, jsonData, 0644); err != nil {
		return "", fmt.Errorf("failed to write temporary JSON file: %v", err)
	}
	defer os.Remove(tempJSONFile) // Clean up temp file

	// Create a temporary file for the output Markdown
	tempMDFile := filepath.Join(tempDir, "export_output.md")

	// Prepare the Python script to export as Markdown
	script := fmt.Sprintf(`
import json
import sys
from pathlib import Path

# Import rendercv functions
import rendercv.api.functions as rcv_api

# Read CV data from the temporary file
with open('%s', 'r') as f:
    cv_data = json.load(f)

# Create Markdown file
errors = rcv_api.create_a_markdown_file_from_a_python_dictionary(
    cv_data,
    Path('%s')
)

if errors:
    print(f"RenderCV export errors: {errors}", file=sys.stderr)
    sys.exit(1)

print("Markdown export successful")
`, tempJSONFile, tempMDFile)

	// Write the Python script to a temporary file
	scriptFile := filepath.Join(tempDir, "export_md.py")
	if err := os.WriteFile(scriptFile, []byte(script), 0644); err != nil {
		return "", fmt.Errorf("failed to write temporary Python script: %v", err)
	}
	defer os.Remove(scriptFile) // Clean up script file

	// Execute the Python script
	cmd := exec.Command("python3", scriptFile)
	output, err := cmd.CombinedOutput()

	if err != nil {
		return "", fmt.Errorf("failed to execute Python export script: %v, output: %s", err, string(output))
	}

	// Read the generated Markdown file
	mdContent, err := os.ReadFile(tempMDFile)
	if err != nil {
		return "", fmt.Errorf("failed to read generated Markdown file: %v", err)
	}
	defer os.Remove(tempMDFile) // Clean up temp Markdown file

	return string(mdContent), nil
}