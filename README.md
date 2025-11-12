# PDF Merger & Splitter

A simple and user-friendly web application for PDF manipulation built with Python Flask.

## Features
- **Merge PDFs**: Combine multiple PDF files into one (maintains file order)
- **Split PDFs**: Extract specific pages from a PDF file into separate documents

## How to Run
1. Install Python 3.8+ from [python.org](https://python.org)
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python app.py`
4. Open your browser to `http://localhost:5000`

## How to Use
### Merging PDFs
1. Click "Choose Files" and select multiple PDF files
2. Files will be merged in the order they were selected
3. Click "Merge PDFs" to download the combined file

### Splitting PDFs
1. Upload a single PDF file
2. Select the pages you want to extract
3. Click "Split PDF" to download the extracted pages

## Technologies Used
- **Backend**: Python, Flask, PyPDF2
- **Frontend**: HTML, CSS, JavaScript
- **PDF Processing**: PyPDF2 library

## Development
- Run in development mode: `python app.py` (debug mode enabled)
- For production: Use gunicorn with `gunicorn app:app`

## Deployment
This application can be deployed on platforms like:
- Heroku
- Railway
- PythonAnywhere
- DigitalOcean App Platform