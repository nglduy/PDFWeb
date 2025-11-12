# Deployment Guide - Python Flask Version

## Option 1: Heroku (Recommended for beginners)

### Prerequisites
1. Create a free account at [heroku.com](https://heroku.com)
2. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Install [Git](https://git-scm.com/) if not already installed

### Steps
```bash
# 1. Initialize git repository
git init
git add .
git commit -m "Initial commit"

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-pdf-tool-name

# 4. Deploy
git push heroku main

# 5. Open your app
heroku open
```

## Option 2: Railway

### Steps
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Railway will automatically detect Python and deploy!

## Option 3: PythonAnywhere

### Steps
1. Create account at [pythonanywhere.com](https://pythonanywhere.com)
2. Upload your files via Files tab
3. Create new Web app with Flask
4. Point to your app.py file
5. Install requirements: `pip3.10 install --user -r requirements.txt`

## Option 4: DigitalOcean App Platform

### Steps
1. Go to [digitalocean.com/products/app-platform](https://digitalocean.com/products/app-platform)
2. Connect GitHub repository
3. Select Python/Flask as framework
4. Deploy automatically

## Requirements

Your `requirements.txt` includes:
- Flask==2.3.3
- Flask-CORS==4.0.0
- PyPDF2==3.0.1
- Werkzeug==2.3.7
- gunicorn==21.2.0

## Environment Variables

For production, consider adding:
- `FLASK_ENV=production`
- `PORT` (automatically set by most platforms)

## File Upload Limits

Most free hosting platforms have file size limits:
- Heroku: 50MB request size
- Railway: 100MB
- PythonAnywhere: 100MB (free tier)
- DigitalOcean: 100MB

## Python-Specific Deployment Notes

1. **Runtime**: Most platforms support Python 3.8+
2. **Dependencies**: Use `requirements.txt` for package management
3. **WSGI Server**: Gunicorn is included for production deployment
4. **Static Files**: Flask serves CSS/JS from `/static/` directory

## Troubleshooting

### Common Issues
1. **"Application Error"**: Check logs with `heroku logs --tail`
2. **Import errors**: Ensure all dependencies in requirements.txt
3. **File upload fails**: Check platform file size limits
4. **Static files not loading**: Verify Flask static file configuration

### Performance Tips
1. Use gunicorn with multiple workers: `gunicorn -w 4 app:app`
2. Add file compression for faster uploads
3. Implement file cleanup for temporary files
4. Consider using cloud storage for large files