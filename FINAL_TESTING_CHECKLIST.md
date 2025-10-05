# ✅ Final Testing Checklist - NASA Submission

**Complete this checklist before submitting. Time: 20 minutes**

---

## 🚀 Services Status Check (2 minutes)

### All Services Running?
```powershell
Get-Job | Format-Table Id, State, Command
```

**Expected Result:** 3 jobs running:
- [ ] Backend (port 8000)
- [ ] Frontend (port 8081)
- [ ] Adapter (port 5000)

### Port Accessibility?
```powershell
# Test each port
Invoke-WebRequest -Uri http://localhost:8081 -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5000/api/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:7474 -UseBasicParsing
```

**Expected:** All return status 200

---

## 📄 Page Load Tests (5 minutes)

### 1. Home Page
- [ ] Navigate to http://localhost:8081
- [ ] Hero section loads
- [ ] Navigation bar visible
- [ ] No console errors (F12)

### 2. Research Page
- [ ] Navigate to http://localhost:8081/research
- [ ] Search interface loads
- [ ] Can search for papers
- [ ] Results display correctly

### 3. Knowledge Graph
- [ ] Navigate to http://localhost:8081/knowledge-graph
- [ ] Search bar visible
- [ ] Search for "bone"
- [ ] Graph renders with nodes and edges
- [ ] Can click on nodes

### 4. AI Assistant
- [ ] Navigate to http://localhost:8081/ai-assistant
- [ ] Example questions visible
- [ ] Can click example question
- [ ] Answer appears (2-3 seconds)
- [ ] Shows metadata (paper count, entity count)

### 5. Trends
- [ ] Navigate to http://localhost:8081/trends
- [ ] Publication Timeline tab loads
- [ ] Chart renders correctly
- [ ] Can switch to Emerging Topics tab
- [ ] Can switch to Top Authors tab
- [ ] All charts/tables render

### 6. Features Page
- [ ] Navigate to http://localhost:8081#features
- [ ] Features section visible

### 7. About Page
- [ ] Navigate to http://localhost:8081#about
- [ ] About section visible

---

## 🧪 API Functionality Tests (5 minutes)

### RAG API
```powershell
$body = @{
    question = "What are the effects of microgravity?"
    max_papers = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/chat/ask" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

**Expected:**
- [ ] Returns JSON response
- [ ] Contains `answer` field
- [ ] Contains `metadata` with paper_count
- [ ] No errors

### Trends API
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/trends/timeline?start_year=2020&end_year=2024"
```

**Expected:**
- [ ] Returns timeline data
- [ ] Contains `timeline` array
- [ ] Contains year/count pairs

### Evidence API
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/evidence/all-edges?limit=10"
```

**Expected:**
- [ ] Returns edge list
- [ ] Each edge has evidence_count
- [ ] Contains source/target names

---

## ♿ Accessibility Tests (3 minutes)

### Keyboard Navigation
- [ ] Press Tab repeatedly - highlights move through elements
- [ ] Press Enter on link - navigates to page
- [ ] Press Enter on button - triggers action
- [ ] All focus indicators visible (blue outline)

### Visual Accessibility
- [ ] Text is readable (good contrast)
- [ ] All buttons have clear labels
- [ ] Icons have tooltips or labels
- [ ] No text under 14px font size

### Screen Reader (Optional)
- [ ] Start Windows Narrator (Win + Ctrl + Enter)
- [ ] Navigate through a page
- [ ] Elements are announced properly
- [ ] Images have alt text

---

## 🖥️ Browser Compatibility (2 minutes)

Test in at least 2 browsers:

### Chrome/Edge
- [ ] All pages load
- [ ] Charts render correctly
- [ ] No console errors

### Firefox
- [ ] All pages load
- [ ] Charts render correctly
- [ ] No console errors

---

## 📊 Data Verification (2 minutes)

### Neo4j Database
- [ ] Open http://localhost:7474
- [ ] Run query: `MATCH (n) RETURN count(n)`
- [ ] Result should be ~156 nodes

### Knowledge Graph Data
- [ ] Search "microgravity" in KG
- [ ] Verify ~10+ nodes appear
- [ ] Edges connect related entities

### RAG Data
- [ ] Ask AI: "What is bone loss?"
- [ ] Answer mentions multiple papers
- [ ] Metadata shows paper_count > 0

---

## 🐛 Error Handling Tests (3 minutes)

### Network Errors
- [ ] Stop adapter service temporarily
- [ ] Try to use AI Assistant
- [ ] Error message displays gracefully
- [ ] Restart adapter service

### Invalid Input
- [ ] Submit empty question in AI
- [ ] Button should be disabled
- [ ] Search with special characters
- [ ] No crashes

### Edge Cases
- [ ] Search for non-existent term
- [ ] Displays "no results" message
- [ ] Navigate to invalid URL /nonexistent
- [ ] Shows 404 page

---

## 📸 Documentation Verification (2 minutes)

### README Files
- [ ] SUBMISSION_README.md exists
- [ ] ALL_PRIORITIES_COMPLETE.md exists
- [ ] QUICK_TESTING_GUIDE.md exists
- [ ] SCREENSHOT_GUIDE.md exists
- [ ] All have correct information

### Code Quality
- [ ] No unused imports
- [ ] No TODO comments left
- [ ] No console.log() in production code
- [ ] Proper error handling throughout

---

## 🎯 Final Pre-Submission Checklist

### Technical
- [ ] All 3 services running without errors
- [ ] All 7 pages load correctly
- [ ] All API endpoints working
- [ ] No console errors in browser
- [ ] Neo4j database populated (156 nodes)

### Features
- [ ] Priority 1: Knowledge Graph ✅
- [ ] Priority 2: RAG AI Assistant ✅
- [ ] Priority 3: Evidence Transparency ✅
- [ ] Priority 4: Trend Analysis ✅
- [ ] Priority 5: Accessibility (80%+) ✅

### Documentation
- [ ] README complete with setup instructions
- [ ] API documentation accessible
- [ ] Architecture diagram/description
- [ ] Screenshots taken (7 essential)

### Presentation
- [ ] Demo script prepared
- [ ] Key talking points identified
- [ ] Value proposition clear
- [ ] Competition advantages highlighted

---

## 🚨 Common Issues & Fixes

### Issue: Service won't start
**Fix:** Check if port is already in use
```powershell
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
Stop-Process -Id <PID> -Force
```

### Issue: Neo4j connection failed
**Fix:** Verify Neo4j is running and password is correct
- Open Neo4j Desktop
- Check database status
- Verify password: `spacebiology123`

### Issue: Frontend won't load
**Fix:** Clear cache and rebuild
```powershell
cd frontend/new\ frontend
npm run build
npm run dev
```

### Issue: Charts not rendering
**Fix:** Check if recharts is installed
```powershell
cd frontend/new\ frontend
npm install recharts --save
```

---

## ✅ Sign-Off

**Tester Name:** _____________  
**Date:** October 5, 2025  
**Time:** _____________  

**All tests passed?** [ ] YES [ ] NO

**Issues found:** _____________________________________________

**Ready to submit?** [ ] YES [ ] NO

---

## 🎉 Submission Readiness Score

Count your checkmarks:
- **90-100%** (80+ checks): 🏆 PERFECT - Submit now!
- **80-89%** (70-79 checks): ✅ EXCELLENT - Minor polish, then submit
- **70-79%** (60-69 checks): ⚠️ GOOD - Fix critical issues first
- **<70%** (<60 checks): ❌ NOT READY - Debug and retest

**Your Score: _____%**

---

**Time to Complete: ~20 minutes**  
**Best Done: Right before submission**  
**Priority: CRITICAL** ⚡
