# 🚀 Deploy to Vercel - Step by Step

## 🎯 Why Vercel?
- ✅ **100% Free** for personal projects
- ✅ **Serverless** - automatic scaling
- ✅ **GitHub integration** - auto-deploy
- ✅ **Global CDN** - fast worldwide
- ✅ **No credit card** required

## 📱 **Quick Deploy (5 minutes)**

### **Method 1: Vercel Website (Easiest)**

1. **Go to Vercel**: Open [vercel.com](https://vercel.com)
2. **Sign up** with your GitHub account
3. **Import Project**: 
   - Click "New Project"
   - Select "Import Git Repository" 
   - Choose `nglduy/PDFWeb`
4. **Deploy**: 
   - Vercel auto-detects Python
   - Click "Deploy"
   - Wait 2-3 minutes
5. **Get Your URL**: `https://your-project.vercel.app`

### **Method 2: Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
vercel login
vercel

# Follow the prompts:
# - Link to existing project? N
# - Project name: pdf-web (or any name)
# - Deploy? Y
```

## 🔧 **Project Structure for Vercel**

```
PDFWeb/
├── api/
│   └── index.py        # Serverless Flask app
├── static/             # CSS & JS files
├── templates/          # HTML templates  
├── vercel.json        # Vercel configuration
└── requirements.txt   # Python dependencies
```

## 🌟 **What You Get**

✅ **Live URL**: `https://your-project.vercel.app`  
✅ **HTTPS Enabled**: Secure by default  
✅ **Global CDN**: Fast loading worldwide  
✅ **Auto-Deploy**: Push to GitHub = Auto-deploy  
✅ **Custom Domain**: Add your own domain later  

## 🛠 **Key Changes Made for Vercel**

1. **Serverless Architecture**: Flask app in `api/index.py`
2. **Memory-based File Storage**: No local file system
3. **Vercel Configuration**: `vercel.json` for routing
4. **Static File Serving**: CSS/JS via Vercel CDN

## 📊 **Vercel Limits (Free Tier)**

- **File Size**: 50MB (perfect for PDFs)
- **Function Timeout**: 10 seconds (enough for PDF processing)
- **Bandwidth**: 100GB/month
- **Deployments**: Unlimited

## 🐛 **Troubleshooting**

### Build Fails?
- Check `requirements.txt` formatting
- Ensure Python 3.8+ compatibility

### Function Timeout?
- Large PDFs (>20MB) might timeout
- Consider upgrading to Pro for 60s timeout

### Static Files Not Loading?
- Ensure files are in `static/` directory
- Check `vercel.json` routing

## 🎉 **After Deployment**

1. **Test Your App**: Try merging and splitting PDFs
2. **Share the URL**: Send to friends and colleagues  
3. **Monitor Usage**: Vercel dashboard shows analytics
4. **Custom Domain**: Add your own domain in settings

**Ready to deploy? Just follow Method 1 above! 🚀**