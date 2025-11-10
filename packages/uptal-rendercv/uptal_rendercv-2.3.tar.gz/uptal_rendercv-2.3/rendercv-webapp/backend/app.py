from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import rendercv.api.functions as rcv_api
from pathlib import Path
import tempfile
import os
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv
from openai import OpenAI
from services import CVService, CVServiceException

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

# Initialize services
cv_service = CVService()

# Temporary storage for PDFs
PDF_DIR = Path("generated_pdfs")
PDF_DIR.mkdir(exist_ok=True)

# Clean up old PDFs on startup
for old_pdf in PDF_DIR.glob("*.pdf"):
    try:
        old_pdf.unlink()
    except:
        pass

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "rendercv-backend"})

@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get available themes."""
    themes = [
        {"id": "classic", "name": "Classic"},
        {"id": "sb2nov", "name": "Sb2nov"},
        {"id": "moderncv", "name": "ModernCV"},
        {"id": "engineeringresumes", "name": "Engineering Resumes"},
        {"id": "engineeringclassic", "name": "Engineering Classic"}
    ]
    return jsonify(themes)

@app.route('/api/render', methods=['POST'])
def render_cv():
    """Generate PDF from CV data."""
    try:
        cv_data = request.json
        
        if not cv_data:
            return jsonify({"error": "No CV data provided"}), 400
        
        # Log the incoming data for debugging
        print(f"Received CV data: {json.dumps(cv_data, indent=2)}")
        
        # Generate unique filename
        pdf_id = f"{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pdf_path = PDF_DIR / f"{pdf_id}.pdf"
        
        # Generate PDF using RenderCV (two-step process: Typst then PDF)
        # First create the Typst file
        typst_path = PDF_DIR / f"{pdf_id}.typ"
        errors = rcv_api.create_a_typst_file_from_a_python_dictionary(
            cv_data,
            typst_path
        )
        
        if not errors:
            # Then render the PDF from the Typst file (it creates PDF in same location)
            import rendercv.renderer.renderer as renderer
            try:
                generated_pdf_path = renderer.render_a_pdf_from_typst(typst_path)
                # Move the PDF to our desired location if needed
                if generated_pdf_path != pdf_path:
                    generated_pdf_path.rename(pdf_path)
                # Clean up the Typst file
                typst_path.unlink(missing_ok=True)
            except Exception as e:
                errors = [{"error": str(e)}]
        
        if errors:
            print(f"RenderCV validation errors: {errors}")
            return jsonify({"error": str(errors)}), 400
        
        # Clean up old PDFs (keep only last 20)
        cleanup_old_pdfs()
        
        return jsonify({
            "success": True,
            "pdf_id": pdf_id,
            "pdf_url": f"/api/pdf/{pdf_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pdf/<pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    """Serve generated PDF."""
    pdf_path = PDF_DIR / f"{pdf_id}.pdf"
    
    if not pdf_path.exists():
        return jsonify({"error": "PDF not found"}), 404
    
    response = send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f"cv_{pdf_id}.pdf"
    )
    
    # Add CORS headers explicitly for PDF responses
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

@app.route('/api/validate', methods=['POST'])
def validate_cv():
    """Validate CV data structure."""
    try:
        cv_data = request.json
        
        # Try to parse with RenderCV
        data_model = rcv_api.read_a_python_dictionary_and_return_a_data_model(cv_data)
        
        if data_model is None:
            return jsonify({
                "valid": False,
                "errors": ["Invalid CV data structure"]
            }), 400
        
        return jsonify({
            "valid": True,
            "message": "CV data is valid"
        })
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "errors": [str(e)]
        }), 400

@app.route('/api/sample/<cv_code>', methods=['GET'])
def get_sample_cv(cv_code):
    """Get CV data from Uptal API using cv_code."""
    try:
        # Use the CV service to fetch data
        cv_data = cv_service.get_cv_by_code(cv_code)
        response = cv_data['data']
        position_match = response.get('position_match', None)

        # check if response is empty return 404
        if not response:
            return jsonify({'error': 'CV not found'}), 404

        # check if enhancement_result is not empty return enhancement_result
        if response.get('enhancement_result'):
            if position_match:
                response['enhancement_result']['position_match'] = position_match
            return jsonify(response['enhancement_result'])
        else:
            return jsonify({'error': 'CV not enhanced'}), 400
        
    except CVServiceException as e:
        # Handle known service exceptions with their specific status codes
        print(f"CV Service error: {e.message}")
        return jsonify({'error': e.message}), e.status_code
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in get_sample_cv: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/info/<cv_code>', methods=['GET'])
def get_info(cv_code):
    """Get info about a CV."""
    try:
        cv_data = cv_service.get_cv_by_code(cv_code)
        return jsonify(cv_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_cv(format):
    """Export CV in different formats."""
    try:
        cv_data = request.json
        
        if format == 'yaml':
            import ruamel.yaml
            yaml = ruamel.yaml.YAML()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(cv_data, f)
                temp_path = f.name
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name='cv.yaml',
                mimetype='text/yaml'
            )
            
        elif format == 'json':
            return jsonify(cv_data)
            
        elif format == 'markdown':
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
                errors = rcv_api.create_a_markdown_file_from_a_python_dictionary(
                    cv_data,
                    Path(f.name)
                )
                if errors:
                    return jsonify({'error': str(errors)}), 400
                    
                return send_file(
                    f.name,
                    as_attachment=True,
                    download_name='cv.md',
                    mimetype='text/markdown'
                )
        else:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_cv():
    """Import CV from YAML file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and file.filename.endswith(('.yaml', '.yml')):
            yaml_content = file.read().decode('utf-8')
            
            # Parse using RenderCV API
            data_model = rcv_api.read_a_yaml_string_and_return_a_data_model(yaml_content)
            
            if data_model is None:
                return jsonify({'error': 'Invalid YAML file'}), 400
            
            cv_data = data_model.model_dump()
            
            return jsonify({
                'success': True,
                'cv_data': cv_data
            })
        else:
            return jsonify({'error': 'Only YAML files are supported'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parse-cv', methods=['POST'])
def parse_cv():
    """Parse CV file using GPT-4o-mini."""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get job analysis and resume answers if provided
        job_analysis_str = request.form.get('job_analysis', '')
        resume_answers_str = request.form.get('resume_answers', '')
        
        job_analysis = None
        resume_answers = None
        
        try:
            if job_analysis_str:
                job_analysis = json.loads(job_analysis_str)
                print(f"Job analysis loaded with {len(job_analysis.get('resume_questions', []))} questions")
            if resume_answers_str:
                resume_answers = json.loads(resume_answers_str)
                print(f"Resume answers loaded: {resume_answers}")
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid job analysis or resume answers format'}), 400
        
        # Check file size (5MB limit)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Check file extension
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY in .env file'}), 500
        
        # Set the API key as environment variable (OpenAI SDK will use it)
        os.environ['OPENAI_API_KEY'] = api_key
        
        try:
            client = OpenAI()
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            # Fallback: try with explicit api_key parameter
            client = OpenAI(api_key=api_key)
        
        # Upload file to OpenAI
        # Convert Flask FileStorage to bytes for OpenAI API
        print(f"Uploading file: {file.filename}")
        file_bytes = file.read()
        file.seek(0)  # Reset file pointer
        
        # Create a tuple with filename and bytes for OpenAI
        file_tuple = (file.filename, file_bytes)
        
        openai_file = client.files.create(
            file=file_tuple,
            purpose="assistants"
        )
        print(f"File uploaded with ID: {openai_file.id}")
        
        # Load the parser prompt
        prompt_path = Path('/app/RESUME_PARSER_PROMPT.md')
        with open(prompt_path, 'r') as f:
            parser_prompt = f.read()
        
        # Build message content
        message_content = [
            {"type": "text", "text": parser_prompt}
        ]
        
        # Add job analysis context if provided
        if job_analysis:
            tailoring_prompt = f"""
## JOB ANALYSIS FOR ADVANCED TAILORING

### Job Description:
{job_analysis.get('description', '')}

### Key Requirements (by importance):
"""
            # Add requirements sorted by importance
            requirements = job_analysis.get('requirements', [])
            for req in sorted(requirements, key=lambda x: x.get('importance', 0), reverse=True):
                tailoring_prompt += f"- [{req.get('importance', 0)}%] {req.get('requirement', '')}\n"
            
            tailoring_prompt += "\n### Nice-to-Have Skills (by importance):\n"
            nice_to_have = job_analysis.get('nice_to_have', [])
            for nth in sorted(nice_to_have, key=lambda x: x.get('importance', 0), reverse=True):
                tailoring_prompt += f"- [{nth.get('importance', 0)}%] {nth.get('nice_to_have', '')}\n"
            
            if job_analysis.get('required_industry'):
                tailoring_prompt += f"\n### Required Industry: {job_analysis['required_industry']}\n"
            
            if job_analysis.get('minimum_years_of_experience'):
                tailoring_prompt += f"### Minimum Years of Experience: {job_analysis['minimum_years_of_experience']}\n"
            
            # Add resume answers if provided
            if resume_answers and job_analysis.get('resume_questions'):
                tailoring_prompt += "\n## CANDIDATE'S RESPONSES TO ROLE-SPECIFIC QUESTIONS:\n"
                tailoring_prompt += "These answers provide crucial context about the candidate's relevant experience. Use them to:\n"
                tailoring_prompt += "- Identify which experiences to emphasize\n"
                tailoring_prompt += "- Understand the depth of their expertise in required areas\n"
                tailoring_prompt += "- Determine the order of bullet points and sections\n\n"
                
                questions = job_analysis.get('resume_questions', [])
                for idx, question in enumerate(questions):
                    # Check for both string and numeric keys
                    answer = resume_answers.get(str(idx)) or resume_answers.get(idx)
                    if answer:
                        tailoring_prompt += f"\n**Q{idx + 1}: {question}**\n"
                        tailoring_prompt += f"Answer: {answer}\n"
                        tailoring_prompt += "---\n"
            
            tailoring_prompt += """
## ADVANCED TAILORING INSTRUCTIONS:

### PRIMARY DIRECTIVE FOR QUESTION ANSWERS:
If the candidate has provided answers to the role-specific questions above, these answers are CRITICAL for tailoring. You MUST:
1. Identify the specific experiences, projects, and achievements mentioned in their answers
2. Ensure these mentioned items appear prominently in the relevant sections
3. Reorder bullet points so that answer-related content appears first
4. Use the exact terminology and metrics they provided in their answers
5. In the summary section, directly reference the key points from their answers

### GENERAL TAILORING GUIDELINES:
1. **Prioritize by Importance**: Focus on requirements with higher importance scores
2. **Answer Integration**: The candidate's question answers reveal what THEY consider most relevant - prioritize these items
3. **Industry Alignment**: Emphasize experiences and skills from the required industry
4. **Experience Level**: Ensure the years of experience is prominently displayed if it meets/exceeds the minimum
5. **Keyword Optimization**: Use keywords from both requirements and nice-to-have sections naturally
6. **Summary Customization**: 
   - Lead with points that directly address the questions they answered
   - Include specific achievements they highlighted in their answers
   - Mirror the language they used in their responses
7. **Highlight Ordering**: 
   - FIRST: Experiences directly mentioned in their question answers
   - SECOND: Other experiences matching high-importance requirements
   - THIRD: General relevant experiences
8. **Skills Emphasis**: If they mentioned specific tools/technologies in answers, ensure these appear in skills

### CRITICAL RULES:
- DO NOT fabricate any information not present in the original resume
- DO NOT add new experiences beyond what's in the source material
- The question answers guide WHAT to emphasize, not what to invent
- Maintain complete accuracy while using answers to determine priority
- If an answer mentions a specific project/achievement, that MUST be prominently featured
"""
            message_content.append({"type": "text", "text": tailoring_prompt})
        
        # Add final instructions based on whether we're tailoring or not
        if job_analysis and resume_answers:
            final_instruction = """
IMPORTANT: You must now parse AND tailor the following resume file based on:
1. The job analysis requirements provided above
2. The candidate's specific answers to role questions
3. The tailoring guidelines in your prompt

The candidate's answers are CRITICAL - they indicate what experiences are most relevant.
Ensure these specific experiences appear prominently in the output.

Parse and tailor the resume file below, returning ONLY the JSON object:"""
        elif job_analysis:
            final_instruction = """
Parse AND tailor the following resume file based on the job analysis requirements above.
Focus on highlighting experiences that match the high-importance requirements.
Return ONLY the JSON object:"""
        else:
            final_instruction = "Parse the following resume file and return ONLY the JSON object:"
        
        message_content.extend([
            {"type": "text", "text": final_instruction},
            {"type": "text", "text": f"File: {file.filename}"},
            {
                "type": "file",
                "file": {
                    "file_id": openai_file.id
                }
            }
        ])
        
        # Process with GPT-4o-mini
        print(f"Processing with GPT-4o-mini... (with job analysis: {bool(job_analysis)}, with answers: {bool(resume_answers)})")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            temperature=0.1,  # Lower temperature for more consistent parsing
            max_tokens=4000
        )
        
        # Extract the response
        parsed_content = response.choices[0].message.content
        print(f"GPT response received: {len(parsed_content)} characters")
        
        # Clean up - delete file from OpenAI
        try:
            client.files.delete(openai_file.id)
            print(f"Deleted file from OpenAI: {openai_file.id}")
        except:
            pass  # Non-critical if delete fails
        
        # Parse the JSON response
        try:
            # Try to extract JSON from the response (in case there's extra text)
            import re
            json_match = re.search(r'\{[\s\S]*\}', parsed_content)
            if json_match:
                parsed_content = json_match.group()
            
            cv_data = json.loads(parsed_content)
            
            # Validate the structure has required fields
            if 'cv' not in cv_data or 'design' not in cv_data:
                raise ValueError("Invalid CV structure")
            
            if 'name' not in cv_data['cv'] or not cv_data['cv']['name']:
                raise ValueError("Name is required")
            
            return jsonify({
                'success': True,
                'cv_data': cv_data
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {parsed_content[:500]}...")  # Log first 500 chars
            return jsonify({'error': 'Failed to parse AI response as JSON'}), 500
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
            
    except Exception as e:
        print(f"Error in parse_cv: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/cv-enhance/<cv_code>/edits', methods=['POST'])
def update_cv_edits(cv_code):
    """
    Update CV with new data via external API.

    User edits their CV in the editor and submits JSON data.

    Process:
    1. Validate JSON data
    2. Generate PDF from JSON using RenderCV
    3. Call cv_service.update_cv_edits() which triggers:
       - Old CV file deleted from storage
       - New CV uploaded
       - CV text extracted
       - CV data re-parsed
       - Database record updated (cv_path, cv_data, status, cv_enhance_status)
       - CV Enhancement Job dispatched
       - CV Analysis Job dispatched
       - Socket Event: cv_updated emitted

    Returns:
        JSON response with:
        - status: success/error
        - data: {cv_code, cv_id, application_id, status, cv_updated, message}
    """
    try:
        # Validate JSON data
        cv_data = request.json
        
        if not cv_data:
            return jsonify({
                'status': 'error',
                'error': 'No CV data provided'
            }), 400

        # Log the incoming data for debugging
        print(f"Received CV data for enhancement: {json.dumps(cv_data, indent=2)}")
        
        # Generate PDF from JSON using RenderCV
        # Create a temporary Typst file
        pdf_id = f"{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        typst_path = PDF_DIR / f"{pdf_id}.typ"
        pdf_path = PDF_DIR / f"{pdf_id}.pdf"
        
        # Step 1: Create Typst file from CV data
        errors = rcv_api.create_a_typst_file_from_a_python_dictionary(
            cv_data,
            typst_path
        )
        
        if errors:
            print(f"RenderCV validation errors: {errors}")
            return jsonify({
                'status': 'error',
                'error': f'Invalid CV data: {str(errors)}'
            }), 400

        # Step 2: Render PDF from Typst file
        import rendercv.renderer.renderer as renderer
        try:
            generated_pdf_path = renderer.render_a_pdf_from_typst(typst_path)
            # Move the PDF to our desired location if needed
            if generated_pdf_path != pdf_path:
                generated_pdf_path.rename(pdf_path)
            # Clean up the Typst file
            typst_path.unlink(missing_ok=True)
        except Exception as e:
            # Clean up on error
            typst_path.unlink(missing_ok=True)
            return jsonify({
                'status': 'error',
                'error': f'PDF generation failed: {str(e)}'
            }), 500
        
        # Validate PDF was created
        if not pdf_path.exists():
            return jsonify({
                'status': 'error',
                'error': 'PDF generation failed'
            }), 500

        # Validate file size (max 5MB)
        file_size = pdf_path.stat().st_size
        if file_size > 5 * 1024 * 1024:  # 5MB
            pdf_path.unlink()  # Clean up
            return jsonify({
                'status': 'error',
                'error': 'Generated PDF exceeds 5MB limit'
            }), 400

        # Convert PDF to file-like object for the service
        with open(pdf_path, 'rb') as pdf_file:
            # Read the PDF content
            pdf_content = pdf_file.read()
        
        # Create a file-like object from the PDF bytes
        from io import BytesIO
        from werkzeug.datastructures import FileStorage
        
        cv_file = FileStorage(
            stream=BytesIO(pdf_content),
            filename=f"{cv_data.get('cv', {}).get('name', 'CV').replace(' ', '_')}_{pdf_id}.pdf",
            content_type='application/pdf'
        )
        
        # Call cv_service to update CV via external API
        # The API handles:
        # - Deleting old CV file
        # - Uploading new CV
        # - Extracting text
        # - Re-parsing data
        # - Updating database
        # - Dispatching jobs
        # - Emitting socket events
        result = cv_service.update_cv_edits(cv_code, cv_file)

        # Clean up the temporary PDF file
        try:
            pdf_path.unlink()
        except:
            pass  # Non-critical if cleanup fails
        
        return jsonify(result), 200

    except CVServiceException as e:
        return jsonify({
            'status': 'error',
            'error': e.message
        }), e.status_code
    except Exception as e:
        print(f"Error in update_cv_edits: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f'Server error: {str(e)}'
        }), 500

def cleanup_old_pdfs(keep_count=20):
    """Remove old PDFs, keeping only the most recent ones."""
    try:
        pdf_files = sorted(PDF_DIR.glob('*.pdf'), key=lambda x: x.stat().st_mtime, reverse=True)
        for old_file in pdf_files[keep_count:]:
            old_file.unlink()
    except Exception as e:
        print(f"Error cleaning up PDFs: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)