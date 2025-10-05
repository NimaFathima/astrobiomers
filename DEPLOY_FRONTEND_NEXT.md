# 🌐 DEPLOY FRONTEND TO VERCEL (10 minutes)

## ⚠️ IMPORTANT: Do this AFTER backend is deployed!

You need your backend URL first. If you haven't deployed the backend yet, see `DEPLOY_BACKEND_NOW.md`.

---

## 🚀 VERCEL DEPLOYMENT STEPS

### Step 1: Sign Up for Vercel
1. Go to: https://vercel.com/signup
2. Click **"Continue with GitHub"**
3. Authorize Vercel to access your GitHub
4. You're in!

### Step 2: Import Project
1. On Vercel dashboard, click **"Add New..."** → **"Project"**
2. You'll see your GitHub repositories
3. Find **"astrobiomers"**
4. Click **"Import"**

### Step 3: Configure Project Settings

**Framework Preset:**
```
Vite
```
(Should auto-detect this)

**Root Directory:**
```
frontend/new frontend
```
⚠️ **IMPORTANT**: Click "Edit" next to Root Directory and set this!

**Build Command:**
```
npm run build
```
(Should be auto-filled)

**Output Directory:**
```
dist
```
(Should be auto-filled)

**Install Command:**
```
npm install
```
(Should be auto-filled)

### Step 4: Add Environment Variable

Click **"Environment Variables"** section.

Add this variable:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://astrobiomers-backend.onrender.com` |

⚠️ **Replace with YOUR actual backend URL from Render!**

### Step 5: Deploy!
1. Click **"Deploy"**
2. Vercel will start building...
3. **Wait 2-3 minutes**
4. You'll see: **"Congratulations! 🎉"**

### Step 6: Get Your Live URL
At the top, you'll see:
```
https://astrobiomers.vercel.app
```

Or similar (Vercel assigns random URL if name is taken)

### Step 7: Test Your Website!
1. Visit your Vercel URL
2. You should see the homepage with space background ✅
3. Click "Features" - should work ✅
4. Click "Knowledge Graph" - should load ✅
5. Try searching for "stem cells" ✅

---

## 🔧 IF SOMETHING DOESN'T WORK

### Issue: Knowledge Graph not loading
**Solution**: Update backend CORS

I'll help you update `backend/main.py` to allow your Vercel URL.

Reply with:
```
"My Vercel URL is: https://astrobiomers.vercel.app"
```

And I'll create a CORS fix for you!

### Issue: API calls failing
**Check**:
1. Is backend URL correct in environment variables?
2. Does backend URL end with `.onrender.com`? (no trailing slash!)
3. Is backend still running? Visit `YOUR_BACKEND_URL/health`

---

## 🎯 FINAL RESULT

After deployment, you'll have:

```
✅ Live Website:     https://astrobiomers.vercel.app
✅ Backend API:      https://astrobiomers-backend.onrender.com
✅ Database:         Neo4j Aura (cloud)
✅ Source Code:      https://github.com/NimaFathima/astrobiomers
```

**Share the Vercel URL with NASA!** 🚀

---

## 📝 VERCEL FREE TIER BENEFITS

- ✅ Unlimited deployments
- ✅ 100GB bandwidth per month
- ✅ Automatic HTTPS
- ✅ Global CDN (super fast!)
- ✅ Automatic builds on git push
- ✅ Preview deployments for every commit
- ✅ Custom domains (if you want)

---

## ⏰ TIME ESTIMATE

- Sign up: 1 minute
- Configure: 3 minutes
- Build & deploy: 2-3 minutes
- Testing: 2 minutes
- **Total: ~10 minutes**

---

## 🎉 WHEN YOU'RE DONE

Reply with:

**"Website is live at: https://astrobiomers.vercel.app"**

And I'll help you:
1. Update backend CORS (if needed)
2. Create NASA submission README
3. Take screenshots for submission
4. Prepare video demo script

**You're almost there!** 🌟
