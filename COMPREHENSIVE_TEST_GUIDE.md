# 🧪 Comprehensive Web Application Testing Guide

**Date:** October 5, 2025  
**Status:** Both servers running  
**URLs:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Neo4j: Cloud (Aura) - neo4j+s://d3ff59a7.databases.neo4j.io

---

## ✅ Server Status

### Backend (FastAPI)
- **Status:** ✅ Running (Process 13936)
- **Port:** 8000
- **Database:** Neo4j Aura connected
- **Recent Fixes:**
  - ✅ DEMO papers filtered from search
  - ✅ URL generation handles PMC/PMID/DEMO correctly
  - ⚠️ Note: Occasional Neo4j timeout (connection reset) - retry if needed

### Frontend (Vite + React)
- **Status:** ✅ Running
- **Port:** 8080
- **Network:** Also accessible at http://192.168.29.130:8080/

---

## 🎯 Testing Checklist

### 1. Home Page (Dashboard) ✓
**URL:** http://localhost:8080/

**Tests:**
- [ ] Page loads without errors
- [ ] Hero section displays properly
- [ ] Navigation bar works
- [ ] All cards/sections visible
- [ ] Responsive layout works (try resizing)

**Expected:**
- Welcome message
- Overview of features
- Navigation to all sections

---

### 2. Knowledge Graph 🔬
**URL:** http://localhost:8080/knowledge-graph

**Tests:**
- [ ] **Search Functionality**
  - Type "stem cell" in search box
  - Graph should load with nodes and links
  - Should see only REAL papers (no DEMO_X papers)
  
- [ ] **Graph Visualization**
  - Nodes appear (green for papers, blue/purple for entities)
  - Links connect nodes
  - Can pan and zoom
  - Nodes are interactive (hover shows info)

- [ ] **Paper Interaction**
  - Click on a paper node (green)
  - Modal should open with paper details
  - Should show: Title, Authors, Abstract, Journal, Year
  - "Open Full Article" button present

- [ ] **Article Links**
  - For PMC papers (e.g., PMC7998608):
    - Click "Open Full Article"
    - Should open https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7998608/
    - Real article should display
  
  - For PMID papers (numeric IDs):
    - Click "Open Full Article"
    - Should open PubMed link
    - Article should display

- [ ] **No More Errors**
  - ✅ No "about:blank" pages
  - ✅ No "Not found" errors from DEMO papers
  - ✅ No duplicate DEMO papers in results

**Search Terms to Try:**
- "stem cell"
- "microgravity"
- "space biology"
- "radiation"
- "muscle atrophy"

---

### 3. AI Assistant 🤖
**URL:** http://localhost:8080/assistant

**Tests:**
- [ ] Page loads
- [ ] Chat interface visible
- [ ] Can type messages
- [ ] Send button works

**Questions to Ask:**
- "What research has been done on stem cells in space?"
- "Tell me about microgravity effects on human biology"
- "What are the health risks of space travel?"

**Expected:**
- AI responds with relevant information
- Cites papers from knowledge graph
- Provides scientific answers
- Response time reasonable (< 10 seconds)

---

### 4. Research Papers 📚
**URL:** http://localhost:8080/papers

**Tests:**
- [ ] Papers list loads
- [ ] Can see multiple papers
- [ ] Each paper shows: Title, Authors, Abstract preview
- [ ] Can click to view details
- [ ] Search/filter works (if implemented)

**Expected:**
- List of real papers (no DEMO papers)
- Proper formatting
- Links work

---

### 5. Data Pipeline ⚙️
**URL:** http://localhost:8080/pipeline

**Tests:**
- [ ] Pipeline status page loads
- [ ] Shows pipeline stages/steps
- [ ] Indicates what's complete
- [ ] May show data import history

**Expected:**
- Visual representation of data flow
- Status indicators
- Information about data sources

---

### 6. About/Documentation 📖
**URL:** http://localhost:8080/about (or similar)

**Tests:**
- [ ] About page loads
- [ ] Project description present
- [ ] Team information (if applicable)
- [ ] Links to GitHub, documentation work

**Expected:**
- Clear project explanation
- Credits and acknowledgments
- Contact information

---

### 7. Settings/Profile ⚙️
**URL:** http://localhost:8080/settings (if exists)

**Tests:**
- [ ] Settings page accessible
- [ ] Can change preferences
- [ ] Changes persist

---

## 🐛 Known Issues (Recently Fixed)

### ✅ Fixed Issues:
1. ✅ **DEMO Papers Causing Errors**
   - **Was:** DEMO_4 papers tried to open invalid PubMed URLs
   - **Fix:** DEMO papers now filtered from search results entirely

2. ✅ **Blank Article Pages**
   - **Was:** "Open Full Article" went to about:blank
   - **Fix:** URL generation now handles PMC vs PMID correctly

3. ✅ **Duplicate Papers**
   - **Was:** Same papers appearing multiple times
   - **Fix:** DEMO papers removed, deduplication improved

### ⚠️ Current Issues:
1. **Neo4j Connection Timeouts**
   - **Symptom:** Occasional "Connection reset" errors
   - **Impact:** Knowledge Graph search may fail
   - **Workaround:** Wait a few seconds and try again
   - **Cause:** Neo4j Aura cloud connection gets reset after inactivity

---

## 🔍 Detailed Testing Scenarios

### Scenario A: First-Time User Experience
1. Open http://localhost:8080
2. Navigate through all pages using nav bar
3. Explore Knowledge Graph with "stem cell" search
4. Click on a paper, read details, open article
5. Ask AI assistant a question
6. Browse papers list

**Success Criteria:**
- No errors in console
- All pages load within 3 seconds
- Navigation smooth
- Data displays correctly

---

### Scenario B: Knowledge Graph Deep Dive
1. Search for "microgravity"
2. Identify paper nodes (green) vs entity nodes (blue/purple)
3. Click on 3 different papers
4. Verify each shows unique details
5. Click "Open Full Article" on each
6. Verify articles open correctly

**Success Criteria:**
- No DEMO papers appear
- All article links work
- No "Not found" errors
- Papers show real scientific content

---

### Scenario C: AI Assistant Usage
1. Ask: "What does the research say about stem cells in microgravity?"
2. Wait for response
3. Check if response cites specific papers
4. Ask follow-up: "Tell me more about the first paper"
5. Verify AI maintains context

**Success Criteria:**
- AI provides relevant, scientific answers
- Cites papers from knowledge graph
- Maintains conversation context
- No timeout errors

---

## 📊 Performance Benchmarks

### Expected Performance:
- **Home Page Load:** < 2 seconds
- **Knowledge Graph Search:** < 3 seconds (first search may take longer)
- **Paper Modal Open:** < 1 second
- **AI Assistant Response:** 5-15 seconds
- **Page Navigation:** < 1 second

---

## 🚨 Error Monitoring

### Check Browser Console:
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for errors (red messages)

### Common Errors to Ignore:
- Neo4j deprecation warnings (about `id()` vs `elementId()`)
- CORS preflight (if OPTIONS requests shown)

### Errors to Report:
- 500 Internal Server Error
- 404 Not Found (unless you search for non-existent term)
- Frontend crash/white screen
- "Failed to fetch" errors

---

## 🔧 Quick Troubleshooting

### If Knowledge Graph Doesn't Load:
1. Check backend terminal for errors
2. Look for "Connection reset" message
3. Wait 10 seconds, try again
4. If persists, restart backend:
   ```powershell
   Stop-Process -Name python -Force
   cd C:\Users\mi\Downloads\ASTROBIOMERS\backend
   python main.py
   ```

### If Frontend Doesn't Load:
1. Check if Vite server running (terminal shows "ready in X ms")
2. Try refreshing page (Ctrl+R)
3. Clear cache (Ctrl+Shift+R)
4. If persists, restart frontend:
   ```powershell
   cd "C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend"
   npm run dev
   ```

### If Both Servers Stop:
Run this command:
```powershell
# Backend (in one terminal)
cd C:\Users\mi\Downloads\ASTROBIOMERS\backend; python main.py

# Frontend (in another terminal)
cd "C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend"; npm run dev
```

---

## ✅ Test Completion Checklist

After completing all tests, verify:

- [ ] All 6+ pages accessible
- [ ] No console errors (except known warnings)
- [ ] Knowledge Graph works with real papers
- [ ] AI Assistant responds appropriately
- [ ] All article links open correctly
- [ ] No DEMO papers visible
- [ ] Navigation smooth between pages
- [ ] Responsive design works (mobile/tablet/desktop)

---

## 📝 Test Report Template

**Date:** October 5, 2025  
**Tester:** [Your Name]  
**Duration:** [Testing time]

### Pages Tested:
- [ ] Home ✅/❌
- [ ] Knowledge Graph ✅/❌
- [ ] AI Assistant ✅/❌
- [ ] Research Papers ✅/❌
- [ ] Data Pipeline ✅/❌
- [ ] About/Docs ✅/❌

### Critical Issues Found:
1. [Issue description]
2. [Issue description]

### Minor Issues Found:
1. [Issue description]
2. [Issue description]

### Overall Assessment:
- **Functionality:** [Excellent/Good/Fair/Poor]
- **Performance:** [Excellent/Good/Fair/Poor]
- **User Experience:** [Excellent/Good/Fair/Poor]
- **Ready for Production:** [Yes/No - because...]

---

## 🎉 Success Indicators

Your application is working correctly if:

1. ✅ Knowledge Graph displays real papers only
2. ✅ All paper article links work (no 404 errors)
3. ✅ AI Assistant provides intelligent responses
4. ✅ No crashes or white screens
5. ✅ Navigation works smoothly
6. ✅ Data loads within reasonable time
7. ✅ No DEMO papers visible to users
8. ✅ Console shows minimal errors

---

## 🚀 Next Steps After Testing

If all tests pass:
1. Document any minor issues
2. Consider deployment to production
3. Prepare for NASA Space Apps submission
4. Create screenshots for documentation
5. Record demo video

If issues found:
1. Document each issue clearly
2. Note steps to reproduce
3. Report back for fixes
4. Re-test after fixes applied

---

**Happy Testing! 🧪🚀**
