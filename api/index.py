from flask import Flask, request, jsonify, send_file
import io
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Simple in-memory cache for PDF data
pdf_cache = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def generate_filename(original_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = secure_filename(original_name)
    return f"{timestamp}_{name}"

@app.route('/', methods=['GET'])
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Tools</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        input[type="file"] { margin: 10px 0; }
        #status { margin: 10px 0; font-weight: bold; }
    </style>
</head>
<body>
    <h1>PDF Merger & Splitter</h1>
    
    <div class="section">
        <h2>Merge PDFs</h2>
        <input type="file" id="mergeFiles" multiple accept=".pdf">
        <br>
        <button class="btn" onclick="mergePDFs()">Merge PDFs</button>
        <div id="mergeStatus"></div>
    </div>
    
    <div class="section">
        <h2>Split PDF</h2>
        <input type="file" id="splitFile" accept=".pdf">
        <br>
        <div id="pdfInfo" style="display:none;">
            <p id="pageCount"></p>
            <input type="text" id="pageNumbers" placeholder="Enter pages (e.g., 1,3,5-8)">
            <br>
            <button class="btn" onclick="splitPDF()">Split PDF</button>
        </div>
        <div id="splitStatus"></div>
    </div>

    <script>
        let currentPdfData = null;

        document.getElementById('splitFile').addEventListener('change', function(e) {
            if (e.target.files[0]) {
                analyzePDF(e.target.files[0]);
            }
        });

        async function mergePDFs() {
            const files = document.getElementById('mergeFiles').files;
            if (files.length < 2) {
                alert('Please select at least 2 PDF files');
                return;
            }

            document.getElementById('mergeStatus').textContent = 'Merging...';

            const formData = new FormData();
            for (let file of files) {
                formData.append('pdfs', file);
            }

            try {
                const response = await fetch('/api/merge', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, 'merged.pdf');
                    document.getElementById('mergeStatus').textContent = 'Success!';
                } else {
                    const error = await response.text();
                    document.getElementById('mergeStatus').textContent = 'Error: ' + error;
                }
            } catch (error) {
                document.getElementById('mergeStatus').textContent = 'Error: ' + error.message;
            }
        }

        async function analyzePDF(file) {
            document.getElementById('splitStatus').textContent = 'Analyzing...';

            const formData = new FormData();
            formData.append('pdf', file);

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('pageCount').textContent = `Pages: ${result.pageCount}`;
                    document.getElementById('pdfInfo').style.display = 'block';
                    currentPdfData = result;
                    document.getElementById('splitStatus').textContent = '';
                } else {
                    const error = await response.text();
                    document.getElementById('splitStatus').textContent = 'Error: ' + error;
                }
            } catch (error) {
                document.getElementById('splitStatus').textContent = 'Error: ' + error.message;
            }
        }

        async function splitPDF() {
            if (!currentPdfData) {
                alert('Please upload a PDF first');
                return;
            }

            const pageInput = document.getElementById('pageNumbers').value;
            const pages = parsePages(pageInput);

            if (pages.length === 0) {
                alert('Please enter valid page numbers');
                return;
            }

            document.getElementById('splitStatus').textContent = 'Splitting...';

            try {
                const response = await fetch('/api/split', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filename: currentPdfData.filename,
                        pages: pages
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, `split_pages_${pages.join('_')}.pdf`);
                    document.getElementById('splitStatus').textContent = 'Success!';
                } else {
                    const error = await response.text();
                    document.getElementById('splitStatus').textContent = 'Error: ' + error;
                }
            } catch (error) {
                document.getElementById('splitStatus').textContent = 'Error: ' + error.message;
            }
        }

        function parsePages(input) {
            const pages = [];
            const parts = input.split(',');
            
            for (let part of parts) {
                part = part.trim();
                if (part.includes('-')) {
                    const [start, end] = part.split('-').map(n => parseInt(n.trim()));
                    for (let i = start; i <= end; i++) {
                        pages.push(i);
                    }
                } else {
                    const num = parseInt(part);
                    if (!isNaN(num)) pages.push(num);
                }
            }
            
            return [...new Set(pages)].sort((a, b) => a - b);
        }

        function downloadFile(blob, filename) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
    </script>
</body>
</html>
    '''

@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    try:
        files = request.files.getlist('pdfs')
        
        if len(files) < 2:
            return 'At least 2 files required', 400
        
        pdf_writer = PdfWriter()
        
        for file in files:
            if not allowed_file(file.filename):
                return f'Invalid file: {file.filename}', 400
                
            file_bytes = file.read()
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')
        
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/api/analyze', methods=['POST'])
def analyze_pdf():
    try:
        file = request.files['pdf']
        
        if not allowed_file(file.filename):
            return 'Invalid file', 400
            
        file_bytes = file.read()
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(pdf_reader.pages)
        
        filename = generate_filename(file.filename)
        pdf_cache[filename] = file_bytes
        
        return jsonify({
            'pageCount': page_count,
            'filename': filename
        })
        
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/api/split', methods=['POST'])
def split_pdf():
    try:
        data = request.get_json()
        filename = data['filename']
        pages = data['pages']
        
        if filename not in pdf_cache:
            return 'PDF not found', 404
            
        file_bytes = pdf_cache[filename]
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(pdf_reader.pages)
        
        # Validate pages
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            return f'Invalid pages: {invalid_pages}', 400
        
        pdf_writer = PdfWriter()
        
        for page_num in sorted(pages):
            page_index = page_num - 1
            pdf_writer.add_page(pdf_reader.pages[page_index])
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        # Clean up
        del pdf_cache[filename]
        
        return send_file(output, mimetype='application/pdf', as_attachment=True, 
                        download_name=f'split_pages_{"_".join(map(str, sorted(pages)))}.pdf')
        
    except Exception as e:
        return f'Error: {str(e)}', 500

# For Vercel
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)