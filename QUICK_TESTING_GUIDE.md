# 🎯 Quick Testing Guide - All Features

**Test all 5 priorities in 15 minutes!**

---

## ✅ Priority 1: Knowledge Graph (COMPLETE)

**Test URL:** http://localhost:8081/knowledge-graph

**What to Test:**
1. Search for "bone loss"
2. See the interactive graph appear
3. Click on nodes to see paper details
4. Verify graph has ~156 nodes

**Expected Result:** Interactive D3.js graph with entities and papers

---

## ✅ Priority 2: RAG AI Assistant (COMPLETE)

**Test URL:** http://localhost:8081/ai-assistant

**What to Test:**
1. Click an example question OR type your own
2. Examples: "What are the effects of microgravity on bone density?"
3. Wait 2-3 seconds for response
4. Check for metadata (paper count, entity count)

**Expected Result:** 
- Answer appears with structured knowledge graph data
- Shows paper count and entity count
- Warning about LLM fallback mode (normal without API key)

---

## ✅ Priority 3: Evidence Transparency (IMPLEMENTED)

**Test URL:** http://localhost:8081/knowledge-graph

**What to Test:**
1. Search for a topic (e.g., "microgravity")
2. Click on an **edge/relationship** between two nodes
3. Evidence modal should appear
4. See supporting papers with PubMed links

**Expected Result:** Modal shows papers supporting that relationship

**Note:** Frontend integration pending - modal component created but needs to be added to KnowledgeGraph.tsx

---

## ✅ Priority 4: Trend Analysis (IMPLEMENTED)

**Test URL:** http://localhost:8081/trends

**What to Test:**

### Tab 1: Publication Timeline
- See area chart of papers per year (2010-2024)
- Check summary cards (Total, Peak Year, Average)

### Tab 2: Emerging Topics
- See bar chart of topics with growth rates
- Check table with detailed breakdowns
- Look for growth rate indicators (2x, 5x, etc.)

### Tab 3: Top Authors
- See table of top 20 authors
- Gold/Silver/Bronze medals for top 3
- Check bar chart distribution

**Expected Result:** Beautiful charts and interactive tables

---

## 🔄 Priority 5: Accessibility (80% COMPLETE)

**What to Test:**

### Keyboard Navigation
1. Press Tab repeatedly - should navigate through all links
2. Press Enter on a link - should navigate
3. Press ESC in a modal - should close (if modal open)

### Visual Accessibility
1. All buttons should have clear focus indicators
2. Text should be readable (good contrast)
3. All interactive elements should be obvious

### Screen Reader (Optional)
1. Turn on Windows Narrator (Win + Ctrl + Enter)
2. Navigate through the app
3. Verify elements are announced properly

**Expected Result:** Full keyboard navigation, visible focus states

---

## 🧪 API Endpoint Tests

### Test RAG API
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/chat/ask" `
  -Method Post `
  -Body '{"question":"What is microgravity?","max_papers":5}' `
  -ContentType "application/json"
```

**Expected:** JSON response with answer, sources, metadata

### Test Trends API
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/trends/timeline?start_year=2020&end_year=2024"
```

**Expected:** Timeline data with yearly counts

### Test Evidence API
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/evidence/all-edges?limit=10"
```

**Expected:** List of edges with evidence counts

---

## ⚠️ Known Issues

1. **No Emerging Topics Found:** Normal with small dataset (148 papers)
   - Solution: Run full pipeline on larger dataset

2. **Evidence Modal Not Integrated:** Component exists but not wired to graph clicks
   - Solution: Add click handler to KnowledgeGraph.tsx (10 minutes)

3. **LLM Fallback Mode:** No OpenAI/Anthropic key configured
   - Solution: Set environment variable (optional)

---

## 🎬 Demo Script (For Video)

### Introduction (30 seconds)
"ASTROBIOMERS is a space biology research engine combining knowledge graphs with AI..."

### Feature 1: Knowledge Graph (1 minute)
1. Navigate to Knowledge Graph
2. Search "radiation"
3. Show interactive graph
4. "This represents 156 entities and 148 research papers..."

### Feature 2: AI Assistant (1 minute)
1. Navigate to AI Assistant
2. Ask "What are the effects of microgravity on bone loss?"
3. Show citation-backed answer
4. "The answer is grounded in our knowledge graph, not hallucinated..."

### Feature 3: Trends (1 minute)
1. Navigate to Trends
2. Show Publication Timeline
3. Show Emerging Topics
4. Show Top Authors
5. "Discover research evolution and collaboration patterns..."

### Conclusion (30 seconds)
"This system democratizes space biology research, accelerates discovery, and promotes scientific rigor through citation transparency."

---

## 📸 Screenshots to Take

1. **Home Page:** Hero section
2. **Knowledge Graph:** Full graph with ~50 nodes visible
3. **AI Assistant:** Chat with answer showing
4. **Trends Timeline:** Area chart
5. **Trends Emerging:** Bar chart with growth rates
6. **Trends Authors:** Top 10 table
7. **Evidence Modal:** (once integrated) Papers supporting a relationship

---

## 🚀 Ready to Submit?

### Final Checklist:
- [ ] All services running (Backend, Frontend, Adapter, Neo4j)
- [ ] Tested all 7 pages
- [ ] Took screenshots
- [ ] Recorded demo video (optional)
- [ ] Read ALL_PRIORITIES_COMPLETE.md
- [ ] Ready to submit!

**Good luck with your NASA Space Apps submission! 🌟**

---

*Quick Test Time: 15 minutes*  
*Full Test Time: 30 minutes*  
*With Screenshots: 45 minutes*  
*With Demo Video: 2.5 hours*
