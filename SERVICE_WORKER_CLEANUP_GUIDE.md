# 🔧 Service Worker Cleanup Guide

## 🚨 Problem: Old Service Worker Still Running

Even though we've disabled the service worker in development mode, your browser may still have the **old service worker cached and running**. Service workers are persistent by design and don't automatically unload.

---

## ✅ Complete Solution (3 Steps)

### **Step 1: Use the Cleanup Tool** 🧹

I've created a special cleanup page for you:

1. **Open**: http://localhost:8080/cleanup.html (should be open now)
2. **Click**: "🚀 Complete Cleanup" button
3. **Wait**: Until you see "Cleanup Complete! ✓"

This will:
- ✅ Unregister all service workers
- ✅ Clear all caches
- ✅ Remove service worker data from localStorage

---

### **Step 2: Hard Refresh the Browser** 🔄

After cleanup, you **MUST** do a hard refresh to clear the browser cache:

**Windows/Linux**:
```
Ctrl + Shift + R
```
or
```
Ctrl + F5
```

**Mac**:
```
Cmd + Shift + R
```
or
```
Cmd + Option + R
```

Do this **twice**:
1. Once on the cleanup page
2. Once on http://localhost:8080

---

### **Step 3: Verify Clean Console** ✅

1. Go to http://localhost:8080
2. Open DevTools: `F12` or `Ctrl+Shift+I`
3. Go to **Console** tab
4. Hard refresh again: `Ctrl+Shift+R`

**Expected Result**: ✅ Clean console with NO errors

---

## 🔍 Manual Verification Steps

If you still see errors, try these manual steps:

### 1. **Check Service Worker Status**

Open DevTools → **Application** tab → **Service Workers**

You should see:
- ✅ "No service workers found" or
- ✅ Service worker status: "Unregistered"

If you see any active service workers:
- Click "Unregister" next to each one
- Hard refresh the page

### 2. **Clear Site Data**

In DevTools → **Application** tab → **Storage**:

Click **"Clear site data"** button

This clears:
- Service workers
- Cache storage
- Local storage
- Session storage
- Cookies
- Indexed DB

### 3. **Disable Cache (Temporary)**

In DevTools → **Network** tab:

Check ☑️ **"Disable cache"** checkbox

Keep DevTools open while testing

---

## 🎯 Understanding the Errors

### **WebSocket Connection Failed**

```
WebSocket connection to 'ws://localhost:8080/?token=...' failed
```

**Why this happens**:
- Old service worker is intercepting WebSocket connections
- Vite HMR (Hot Module Reload) can't connect
- Service worker doesn't know how to handle WebSocket protocol

**Our fix**:
```javascript
// In sw.js - NOW IMPLEMENTED
if (url.protocol === 'ws:' || url.protocol === 'wss:') {
  return; // Skip WebSocket connections
}
```

**But**: Old cached service worker doesn't have this fix yet!

---

### **[Vite] Failed to Connect to WebSocket**

```
[vite] failed to connect to websocket.
your current setup:
(browser) localhost:8080/ <--[HTTP]--> localhost:8080/ (server)
(browser) localhost:8080/ <--[WebSocket (failing)]--> localhost:8080/ (server)
```

**Why this happens**:
- Same as above - old service worker blocking WebSocket
- Prevents hot reload from working

**Solution**: Remove old service worker (Steps 1-3 above)

---

### **Service Worker Fetch Failed**

```
[SW] Fetch failed: TypeError: Failed to fetch
  at cacheFirstStrategy (sw.js:105:35)
```

**Why this happens**:
- Old service worker trying to cache `/src/assets/hero-video.mp4`
- Vite serves this file differently in dev mode
- Service worker doesn't know how to handle it

**Our fix**:
```javascript
// In sw.js - NOW IMPLEMENTED
if (url.pathname.startsWith('/src/') || 
    url.pathname.includes('.mp4') || 
    url.pathname.includes('.webm')) {
  return; // Skip development assets
}
```

**But**: Old cached service worker doesn't have this fix yet!

---

## 🔄 Why Service Workers Are Persistent

Service workers are designed to:
- ✅ Work offline
- ✅ Survive page reloads
- ✅ Persist across browser sessions
- ✅ Cache themselves aggressively

This is **normally good** for offline support, but during development it means:
- ⚠️ Old service worker keeps running even after code changes
- ⚠️ Browser caches the service worker file itself
- ⚠️ Hard to update/remove without manual intervention

---

## 🎯 Our Development Strategy

### **Before (Causing Errors)**:
```javascript
// Service worker always registered
if ('serviceWorker' in navigator) {
  registerServiceWorker(); // ❌ Runs in development too
}
```

### **After (Clean)**:
```javascript
// Service worker only in production
if (import.meta.env.PROD) {
  registerServiceWorker(); // ✅ Only runs in production build
}

// In development: auto-unregister
if (import.meta.env.DEV) {
  navigator.serviceWorker.getRegistrations()
    .then(regs => regs.forEach(reg => reg.unregister()));
}
```

---

## 🧪 Testing the Fix

### **1. After Cleanup Tool**:

Console should show:
```
[App] Service Worker disabled in development mode
[App] Unregistered existing service worker
```

### **2. No More Errors**:

Console should **NOT** show:
- ❌ WebSocket connection failed
- ❌ [Vite] failed to connect
- ❌ [SW] Fetch failed
- ❌ GET hero-video.mp4 404

### **3. Working Features**:

- ✅ Vite HMR works (changes hot reload)
- ✅ Video plays on homepage
- ✅ All pages load correctly
- ✅ No console errors

---

## 🚀 Production vs Development

### **Development (Current)**:
```
✅ Service Worker: DISABLED
✅ Vite HMR: ENABLED
✅ Hot Reload: WORKING
✅ DevTools: Full access
✅ Console: Clean
```

### **Production (After `npm run build`)**:
```
✅ Service Worker: ENABLED
✅ Offline Support: WORKING
✅ Cache Strategy: Active
✅ PWA Features: Enabled
✅ Performance: Optimized
```

---

## 📝 Quick Reference

### **If you still see errors**:

1. ✅ Run cleanup tool: http://localhost:8080/cleanup.html
2. ✅ Hard refresh: `Ctrl+Shift+R` (twice)
3. ✅ Check DevTools → Application → Service Workers
4. ✅ Clear site data if needed
5. ✅ Restart Vite dev server if necessary

### **To restart dev server**:

```powershell
# Stop current server
Ctrl+C (in terminal where Vite is running)

# Start fresh
cd "C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend"
npm run dev
```

---

## 🎉 Expected Final Result

**Clean Console**:
```
[Vite] connected
[App] Service Worker disabled in development mode
[App] Unregistered existing service worker
✨ No errors!
```

**Working Application**:
- ✅ Homepage loads with video
- ✅ Navigation works
- ✅ All pages accessible
- ✅ HMR hot reloads changes
- ✅ Console is clean

---

## 🆘 Still Having Issues?

If errors persist after following all steps:

1. **Close ALL browser tabs** with localhost:8080
2. **Close browser completely**
3. **Reopen browser**
4. **Run cleanup tool again**
5. **Hard refresh twice**

Or try:

1. **Incognito/Private mode** (no cached service worker)
2. **Different browser** (Chrome, Firefox, Edge)
3. **Clear all browser data** (Settings → Privacy → Clear browsing data)

---

## 📚 Additional Resources

- **Cleanup Tool**: http://localhost:8080/cleanup.html
- **Main App**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **Documentation**: `ERROR_FIXES_COMPLETE.md`

---

**Status**: 🎯 Follow these steps and your console will be completely clean!

*Last Updated: October 6, 2025*
