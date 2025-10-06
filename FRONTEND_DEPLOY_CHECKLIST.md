# 🎯 Quick Frontend Deployment Checklist

## ✅ Step-by-Step (5 Minutes)

### 1. Get Backend URL First
- [ ] Go to Render dashboard
- [ ] Find your backend service
- [ ] Copy URL: `https://astrobiomers-______.onrender.com`

### 2. Update Frontend Config
- [ ] I'll update `.env.production` with your backend URL
- [ ] Commit and push to GitHub

### 3. Create Static Site on Render
- [ ] Click "New +" → "Static Site"
- [ ] Select repository: `NimaFathima/astrobiomers`

### 4. Configure Build Settings
```
Name:              astrobiomers-frontend
Branch:            main
Root Directory:    frontend/new frontend
Build Command:     npm install && npm run build
Publish Directory: dist
```

### 5. Add Environment Variable
```
VITE_API_URL = https://your-backend-url.onrender.com/api
```

### 6. Deploy!
- [ ] Click "Create Static Site"
- [ ] Wait 3-5 minutes
- [ ] Get your frontend URL

### 7. Test
- [ ] Open frontend URL
- [ ] Go to Knowledge Graph
- [ ] Search "stem cells"
- [ ] Verify graph loads from backend

---

## 🚀 Let's Start!

**What's your backend URL from Render?**

Or should I help you find it?
