# 📋 FRONTEND DEPLOYMENT - EXACT STEPS

## Copy these values EXACTLY into Render:

---

### 🔧 CONFIGURATION VALUES:

**Name:**
```
astrobiomers-frontend
```

**Branch:**
```
main
```

**Root Directory:**
```
frontend/new frontend
```

**Build Command:**
```
npm install && npm run build
```

**Publish Directory:**
```
dist
```

---

### 🔐 ENVIRONMENT VARIABLE:

Click "Advanced" then "Add Environment Variable":

**Key:**
```
VITE_API_URL
```

**Value (Option 1 - If backend is named "astrobiomers-backend"):**
```
https://astrobiomers-backend.onrender.com/api
```

**Value (Option 2 - Use your actual backend URL):**
```
https://your-actual-backend-url.onrender.com/api
```

---

### ✅ CHECKLIST:

- [ ] Opened Render dashboard
- [ ] Clicked "New +" → "Static Site"
- [ ] Selected `NimaFathima/astrobiomers` repository
- [ ] Filled in Name: `astrobiomers-frontend`
- [ ] Set Branch: `main`
- [ ] Set Root Directory: `frontend/new frontend`
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Publish Directory: `dist`
- [ ] Clicked "Advanced"
- [ ] Added environment variable `VITE_API_URL`
- [ ] Clicked "Create Static Site"
- [ ] Watching build logs...

---

### 🎯 WHAT YOU'LL SEE:

1. **Cloning repository...** (30 seconds)
2. **Running build command...** (2-3 minutes)
3. **Deploying...** (1 minute)
4. **✅ Your site is live!** (You'll get a URL)

---

### 🧪 TEST AFTER DEPLOYMENT:

Your frontend URL will be something like:
```
https://astrobiomers.onrender.com
```

**Test:**
1. Open the URL
2. Should see home page ✅
3. Navigate to different pages ✅
4. Knowledge Graph may not load data yet (normal if backend still building)

---

### 🔗 CONNECT BACKEND & FRONTEND:

**After BOTH are deployed:**

1. Check backend allows your frontend domain
2. Test Knowledge Graph loads data
3. Test all API calls work
4. No CORS errors in console (F12)

---

**START DEPLOYMENT NOW! 🚀**

Just follow the checklist above!
