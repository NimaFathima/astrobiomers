# 🧪 AstroBiomers - Complete Manual Testing Guide

## 🚀 All Services Running Status

### ✅ Services Started:
- **Frontend**: http://localhost:8080 (Vite Dev Server)
- **Backend**: http://localhost:8000 (FastAPI Server)
- **Database**: Neo4j Aura Cloud (Connected)

---

## 📋 Complete Testing Checklist

### 1. HOME PAGE (/) 🏠
**What to test:**
- [ ] Page loads without errors
- [ ] Hero section displays properly
- [ ] Navigation menu works
- [ ] Responsive design on resize

**Expected behavior:**
- Landing page with AstroBiomers branding
- Clean layout with navigation
- No console errors

---

### 2. KNOWLEDGE GRAPH (/knowledge-graph) 🕸️
**What to test:**
- [ ] Search bar appears
- [ ] Enter query: "stem cells"
- [ ] Graph visualization loads
- [ ] Nodes are visible (green = papers, blue/purple = entities)
- [ ] Click on a paper node (green circle)
- [ ] Paper modal opens with details
- [ ] "Open Full Article" button works (opens PubMed/PMC in new tab)
- [ ] Try other queries: "microgravity", "mars", "bacteria"
- [ ] Pan and zoom the graph

**Expected behavior:**
- Interactive D3.js force-directed graph
- Papers clustered with related entities
- Smooth animations
- **NO DEMO papers should appear** (filtered out)
- PMC articles should open correctly

**Common Issues:**
- If graph doesn't load: Check backend is running
- If "Failed to fetch": Check CORS settings
- If demo papers appear: Backend filter not working

---

### 3. SEARCH (/search) 🔍
**What to test:**
- [ ] Search bar is functional
- [ ] Enter: "microgravity effects"
- [ ] Results load
- [ ] Paper cards display
- [ ] Click on a result
- [ ] Details page opens

**Expected behavior:**
- Fast search results
- Relevant papers displayed
- Pagination if many results
- Clean card layout

---

### 4. PAPERS (/papers) 📚
**What to test:**
- [ ] Paper list loads
- [ ] Browse through papers
- [ ] Filter/sort options work
- [ ] Click individual paper
- [ ] Paper details display

**Expected behavior:**
- List of all available papers
- Filters for year, journal, etc.
- Smooth navigation

---

### 5. ENTITIES (/entities) 🧬
**What to test:**
- [ ] Entity list loads
- [ ] Categories displayed (Organisms, Compounds, Conditions, etc.)
- [ ] Click on an entity
- [ ] Related papers shown
- [ ] Entity details display

**Expected behavior:**
- Organized entity categories
- Quick navigation
- Related paper connections

---

### 6. EXPLORATION (/explore) 🗺️
**What to test:**
- [ ] Interactive exploration interface loads
- [ ] Different visualization modes
- [ ] Data filtering options
- [ ] Export functionality (if available)

**Expected behavior:**
- Rich data exploration tools
- Multiple view options
- Responsive interactions

---

### 7. RESOURCES (/resources) 📖
**What to test:**
- [ ] Resource list displays
- [ ] Links to external resources
- [ ] Documentation accessible
- [ ] Download options work

**Expected behavior:**
- Curated resource collection
- Working external links
- Helpful documentation

---

### 8. AI ASSISTANT (/chat or /assistant) 🤖
**What to test:**
- [ ] Chat interface loads
- [ ] Send message: "What are the effects of microgravity on stem cells?"
- [ ] AI response appears
- [ ] Follow-up questions work
- [ ] Chat history maintained
- [ ] Code examples formatted properly (if applicable)

**Expected behavior:**
- Real-time responses
- Context-aware conversations
- Markdown formatting
- Scientific accuracy

---

## 🔧 Backend API Testing

### Test Endpoints Manually:

#### 1. Health Check
```
URL: http://localhost:8000/health
Expected: {"status": "healthy"}
```

#### 2. Knowledge Graph Search
```
URL: http://localhost:8000/api/knowledge-graph?q=stem%20cells
Expected: JSON with nodes and edges
```

#### 3. Paper Details
```
URL: http://localhost:8000/api/paper/{paper_id}
Example: http://localhost:8000/api/paper/PMC7998608
Expected: Paper details JSON
```

#### 4. Search
```
URL: http://localhost:8000/api/search?q=microgravity
Expected: Search results JSON
```

#### 5. AI Chat
```
Method: POST
URL: http://localhost:8000/api/chat
Body: {"message": "Tell me about space biology"}
Expected: AI response JSON
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Failed to fetch" errors
**Solution:**
- Check backend is running: `Get-Process -Name python`
- Check correct port: Backend should be on 8000
- Check CORS settings in backend

### Issue 2: Graph doesn't load
**Solution:**
- Check Neo4j connection in backend logs
- Verify .env file has correct Neo4j credentials
- Check network tab in browser for errors

### Issue 3: DEMO papers appearing
**Solution:**
- Backend should filter them out
- Check knowledge_graph.py has DEMO filter
- Restart backend if needed

### Issue 4: Articles don't open
**Solution:**
- Check paper has valid PMC/PMID
- Verify URL generation logic
- Look for "Not found" errors

### Issue 5: Slow responses
**Solution:**
- Check Neo4j Aura connection speed
- Reduce query complexity
- Check for network issues

---

## ✅ Success Criteria

### Critical Features (Must Work):
- ✅ Frontend loads on localhost:8080
- ✅ Backend API responds on localhost:8000
- ✅ Knowledge Graph displays and is interactive
- ✅ Papers can be clicked and details shown
- ✅ PMC article links open correctly
- ✅ Search returns relevant results
- ✅ No DEMO papers in graph

### Important Features (Should Work):
- ✅ AI Chat provides responses
- ✅ All pages accessible
- ✅ No console errors
- ✅ Responsive design
- ✅ Fast load times

### Nice to Have:
- ✅ Smooth animations
- ✅ Advanced filtering
- ✅ Export functionality
- ✅ Dark mode (if implemented)

---

## 📊 Test Results Template

Copy and fill this out:

```
Date: _____________
Tester: _____________

HOME PAGE:        [ ] Pass  [ ] Fail  Notes: ___________
KNOWLEDGE GRAPH:  [ ] Pass  [ ] Fail  Notes: ___________
SEARCH:           [ ] Pass  [ ] Fail  Notes: ___________
PAPERS:           [ ] Pass  [ ] Fail  Notes: ___________
ENTITIES:         [ ] Pass  [ ] Fail  Notes: ___________
EXPLORATION:      [ ] Pass  [ ] Fail  Notes: ___________
RESOURCES:        [ ] Pass  [ ] Fail  Notes: ___________
AI ASSISTANT:     [ ] Pass  [ ] Fail  Notes: ___________

Overall Status: [ ] All Working  [ ] Issues Found

Critical Issues:
1. ___________
2. ___________

Minor Issues:
1. ___________
2. ___________
```

---

## 🎯 Next Steps After Testing

1. **If all tests pass:** 
   - Application is ready for deployment
   - Document any observations
   - Prepare for production

2. **If issues found:**
   - Document specific errors
   - Check browser console for errors
   - Check backend logs
   - Report issues with details

3. **Performance testing:**
   - Test with multiple simultaneous users
   - Check memory usage
   - Monitor database query times

---

## 📝 Browser Console Checks

Open browser DevTools (F12) and check:
- **Console tab**: No red errors
- **Network tab**: All API calls return 200
- **Application tab**: LocalStorage/SessionStorage used correctly

---

## 🔗 Quick Links

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- Neo4j Browser: https://console.neo4j.io

---

**Happy Testing! 🚀**
