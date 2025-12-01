# 🚀 Deployment Guide - Travel Concierge AI

This guide covers multiple deployment options for your Travel Concierge application.

---

## 📋 Prerequisites

- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- GitHub account (for automated deployments)
- Git repository with your code

---

## ☁️ Option 1: Render (Recommended - Easiest)

**Render offers free tier hosting with automatic deployments from GitHub.**

### Backend Deployment (API)

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Deploy Backend**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `travel-concierge-api`
     - **Region**: Oregon (US West)
     - **Branch**: `main`
     - **Root Directory**: `backend_v2`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add: `GEMINI_API_KEY` = your Gemini API key
   - Save changes

5. **Deploy**
   - Render will automatically build and deploy
   - Get your API URL: `https://travel-concierge-api.onrender.com`

### Frontend Deployment (Static Site)

1. **Deploy Frontend on Render**
   - Click "New +" → "Static Site"
   - Connect same GitHub repository
   - Configure:
     - **Name**: `travel-concierge-frontend`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `dist`

2. **Update API URL**
   - Before deploying, update `frontend/src/components/TripPlanner.jsx` and `ChatInterface.jsx`
   - Change `API_URL` from `http://127.0.0.1:8001` to your Render backend URL

3. **Deploy**
   - Frontend will be live at: `https://travel-concierge-frontend.onrender.com`

**✅ Done! Your app is live on Render (Free tier)**

---

## 🌐 Option 2: Vercel + Render (Frontend + Backend)

**Best for production-ready apps with global CDN.**

### Backend on Render (Same as above)

Follow the Render backend steps above.

### Frontend on Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Update Frontend API URL**
   - Edit `frontend/src/components/TripPlanner.jsx` and `ChatInterface.jsx`
   - Change API_URL to your Render backend URL

3. **Deploy Frontend**
   ```bash
   cd frontend
   vercel
   ```
   
4. **Follow Vercel prompts**
   - Link to your GitHub account
   - Configure project settings
   - Deploy

5. **Set Production Domain**
   ```bash
   vercel --prod
   ```

**✅ Frontend on Vercel, Backend on Render**

---

## 🐳 Option 3: Docker Deployment (Any Platform)

**Deploy to any cloud platform that supports Docker (Railway, Fly.io, etc.)**

### Build Docker Image

```bash
docker build -t travel-concierge-backend .
```

### Run Locally (Test)

```bash
docker run -p 8001:8001 -e GEMINI_API_KEY=your_key travel-concierge-backend
```

### Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Create new project
3. Deploy from GitHub
4. Railway auto-detects Dockerfile
5. Add environment variables
6. Deploy!

### Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set GEMINI_API_KEY=your_key

# Deploy
fly deploy
```

---

## 📱 Option 4: Netlify (Frontend Only)

**Simple drag-and-drop deployment for frontend.**

1. **Build Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `frontend/dist` folder
   - Or connect GitHub for automatic deployments

3. **Configure**
   - Set build command: `npm run build`
   - Set publish directory: `dist`
   - Add redirects (already in `netlify.toml`)

---

## 🔧 Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
APP_NAME=Travel Concierge
VERSION=1.0.0
```

### Frontend
Update API URLs in:
- `frontend/src/components/TripPlanner.jsx`
- `frontend/src/components/ChatInterface.jsx`

Change from:
```javascript
const API_URL = 'http://127.0.0.1:8001'
```

To your deployed backend URL:
```javascript
const API_URL = 'https://your-backend.onrender.com'
```

---

## 🚨 Important Notes

### Free Tier Limitations

- **Render Free**: Spins down after 15 min inactivity (first request takes ~30s)
- **Vercel Free**: Unlimited bandwidth, 100GB/month
- **Netlify Free**: 100GB bandwidth/month

### CORS Configuration

Backend already configured for all origins:
```python
allow_origins=["*"]
```

For production, restrict to your frontend domain:
```python
allow_origins=["https://your-frontend.com"]
```

### API Keys

- Never commit `.env` files to GitHub
- Use platform environment variables
- Rotate keys regularly

---

## 📊 Monitoring Your Deployment

### Check Health
```bash
curl https://your-backend.onrender.com/health
```

### View Metrics
```bash
curl https://your-backend.onrender.com/metrics/summary
```

### Check Logs
- Render: Dashboard → Logs tab
- Vercel: Dashboard → Deployments → Logs
- Railway: Dashboard → Logs

---

## 🎯 Quick Start Summary

**Fastest deployment (5 minutes):**

1. Push code to GitHub
2. Deploy backend on Render (free)
3. Deploy frontend on Vercel (free)
4. Update frontend API_URL
5. Add Gemini API key to Render
6. ✅ Done!

**Your app will be live at:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-api.onrender.com`

---

## 📞 Support

- Render: [render.com/docs](https://render.com/docs)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- Railway: [docs.railway.app](https://docs.railway.app)

---

## 🎉 You're Ready to Deploy!

Choose your preferred platform and follow the steps above. All platforms offer free tiers perfect for demos and portfolios.
