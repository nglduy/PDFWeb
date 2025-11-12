from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import io
from datetime import datetime
import tempfile
import shutil

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB file upload limit
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file is a PDF"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_file(filepath):
    """Safely remove temporary files"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up: {filepath}")
    except Exception as e:
        print(f"Error cleaning up {filepath}: {e}")

def generate_filename(original_name, prefix=""):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(secure_filename(original_name))
    return f"{timestamp}_{prefix}{name}{ext}"

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    """
    Merge multiple PDF files into one
    Expects: multiple PDF files in 'pdfs' field
    Returns: merged PDF file for download
    """
    try:
        # Check if files were uploaded
        if 'pdfs' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('pdfs')
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files are required for merging'}), 400
        
        print(f"Merging {len(files)} PDF files...")
        
        # Create PDF writer for merged result
        pdf_writer = PdfWriter()
        temp_files = []  # Track temporary files for cleanup
        
        try:
            # Process each uploaded file
            for i, file in enumerate(files):
                if file and allowed_file(file.filename):
                    print(f"Processing file {i+1}: {file.filename}")
                    
                    # Save uploaded file temporarily
                    temp_filename = generate_filename(file.filename, f"temp_{i}_")
                    temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
                    file.save(temp_filepath)
                    temp_files.append(temp_filepath)
                    
                    # Read and merge PDF
                    with open(temp_filepath, 'rb') as pdf_file:
                        pdf_reader = PdfReader(pdf_file)
                        
                        # Add all pages from current PDF
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            pdf_writer.add_page(page)
                else:
                    return jsonify({'error': f'Invalid file: {file.filename}. Only PDF files are allowed.'}), 400
            
            # Create merged PDF in memory
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            # Clean up temporary files
            for temp_file in temp_files:
                cleanup_file(temp_file)
            
            print("PDF merge completed successfully")
            
            # Return merged PDF for download
            return send_file(
                output_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='merged.pdf'
            )
            
        except Exception as e:
            # Clean up temporary files on error
            for temp_file in temp_files:
                cleanup_file(temp_file)
            raise e
            
    except Exception as e:
        print(f"Merge error: {e}")
        return jsonify({'error': f'Failed to merge PDFs: {str(e)}'}), 500

@app.route('/pdf-info', methods=['POST'])
def get_pdf_info():
    """
    Get information about uploaded PDF (for splitting)
    Expects: single PDF file in 'pdf' field
    Returns: JSON with page count and file info
    """
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        file = request.files['pdf']
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file. Only PDF files are allowed.'}), 400
        
        print(f"Getting info for: {file.filename}")
        
        # Save uploaded file temporarily
        temp_filename = generate_filename(file.filename, "info_")
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_filepath)
        
        try:
            # Read PDF and get page count
            with open(temp_filepath, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                page_count = len(pdf_reader.pages)
            
            # Return file info (keep file for potential splitting)
            return jsonify({
                'pageCount': page_count,
                'filename': temp_filename,
                'originalName': file.filename
            })
            
        except Exception as e:
            cleanup_file(temp_filepath)
            raise e
            
    except Exception as e:
        print(f"PDF info error: {e}")
        return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 500

@app.route('/split', methods=['POST'])
def split_pdf():
    """
    Split PDF by extracting specific pages
    Expects: JSON with filename and pages array
    Returns: PDF file with selected pages
    """
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data or 'pages' not in data:
            return jsonify({'error': 'Invalid request. Filename and page numbers are required.'}), 400
        
        filename = data['filename']
        pages = data['pages']
        
        if not isinstance(pages, list) or len(pages) == 0:
            return jsonify({'error': 'Invalid page selection. At least one page must be selected.'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'PDF file not found'}), 404
        
        print(f"Splitting PDF: {filename}, extracting pages: {pages}")
        
        try:
            # Read the original PDF
            with open(filepath, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                
                # Validate page numbers (convert from 1-based to 0-based)
                invalid_pages = [p for p in pages if p < 1 or p > total_pages]
                if invalid_pages:
                    return jsonify({
                        'error': f'Invalid page numbers: {invalid_pages}. PDF has {total_pages} pages.'
                    }), 400
                
                # Create new PDF with selected pages
                pdf_writer = PdfWriter()
                
                # Add selected pages (convert 1-based to 0-based indexing)
                for page_num in sorted(pages):
                    page_index = page_num - 1
                    page = pdf_reader.pages[page_index]
                    pdf_writer.add_page(page)
                
                # Create output buffer
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
            
            # Clean up the original file
            cleanup_file(filepath)
            
            # Generate download filename
            sorted_pages = sorted(pages)
            download_name = f"split_pages_{'_'.join(map(str, sorted_pages))}.pdf"
            
            print("PDF split completed successfully")
            
            # Return split PDF for download
            return send_file(
                output_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=download_name
            )
            
        except Exception as e:
            cleanup_file(filepath)
            raise e
            
    except Exception as e:
        print(f"Split error: {e}")
        return jsonify({'error': f'Failed to split PDF: {str(e)}'}), 500

@app.route('/cleanup/<filename>', methods=['DELETE'])
def cleanup_file_endpoint(filename):
    """
    Cleanup endpoint for removing temporary files
    """
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'message': 'File cleaned up successfully'})
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        print(f"Cleanup error: {e}")
        return jsonify({'error': f'Failed to cleanup file: {str(e)}'}), 500

@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler"""
    print(f"Unexpected error: {e}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Add favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return '', 204

# Development server configuration
if __name__ == '__main__':
    print("🚀 PDF Merger & Splitter server starting...")
    print(f"📁 Upload directory: {os.path.abspath(UPLOAD_FOLDER)}")
    print("🌐 Server will be available at: http://localhost:5000")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Check if running in production
    is_production = os.environ.get('RAILWAY_ENVIRONMENT_NAME') or os.environ.get('DYNO') or os.environ.get('RENDER')
    
    # Run the Flask development server
    app.run(
        debug=not is_production,  # Disable debug in production
        host='0.0.0.0',  # Accept connections from any IP
        port=int(os.environ.get('PORT', 5000))  # Use PORT env var or default to 5000
    )