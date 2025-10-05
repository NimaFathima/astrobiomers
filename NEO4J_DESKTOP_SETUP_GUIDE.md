# 🎯 Neo4j Desktop Installation & Setup Guide

**Space Biology Knowledge Engine - Graph Database Deployment**  
**Date:** October 3, 2025  
**Estimated Time:** 10-15 minutes

---

## 📥 Step 1: Download Neo4j Desktop

### 1.1 Visit Neo4j Download Page
Open your browser and go to:
```
https://neo4j.com/download/
```

### 1.2 Select Neo4j Desktop
- Click the **"Download Desktop"** button
- Fill in the form (name, email, company optional)
- Choose **Windows** as your operating system
- Click **"Download Desktop"**

### 1.3 Save Activation Key
After submitting the form, you'll receive:
- **Download link** for the installer
- **Activation Key** (looks like: `eyJhbGciOiJI...`)

⚠️ **IMPORTANT:** Copy and save this activation key - you'll need it!

---

## 🔧 Step 2: Install Neo4j Desktop

### 2.1 Run the Installer
1. Locate the downloaded file: `Neo4j Desktop Setup.exe`
2. Double-click to run the installer
3. If Windows asks "Do you want to allow this app?", click **Yes**

### 2.2 Follow Installation Wizard
1. Click **"Next"** through the welcome screen
2. Accept the license agreement
3. Choose installation location (default is fine)
4. Click **"Install"**
5. Wait for installation to complete (~2-3 minutes)
6. Click **"Finish"**

### 2.3 First Launch
1. Neo4j Desktop will launch automatically
2. **Paste your Activation Key** when prompted
3. Click **"Activate"**

---

## 📊 Step 3: Create Your Database

### 3.1 Create New Project
1. In Neo4j Desktop, you'll see the main interface
2. On the left sidebar, click **"+ New"** next to "Projects"
3. Name it: **"ASTROBIOMERS"**
4. Press Enter

### 3.2 Add Database
1. Click on your **"ASTROBIOMERS"** project
2. In the project view, click **"+ Add"** dropdown
3. Select **"Local DBMS"**

### 3.3 Configure Database
Fill in these details:
- **Name:** `astrobiomers`
- **Password:** `spacebiology123`
- **Version:** Select **5.x** (latest 5.x version, e.g., 5.13 or newer)
- Leave other settings as default

4. Click **"Create"**

---

## ▶️ Step 4: Start Your Database

### 4.1 Start the Database
1. You'll see your `astrobiomers` database in the project
2. Click the **"Start"** button (blue button on the right)
3. Wait ~10-30 seconds for the status to change to **"Active"** (green circle)

### 4.2 Verify Database is Running
You should see:
- ✅ Green circle with **"Active"** status
- Buttons for **"Open"**, **"Stop"**, and settings (•••)

---

## 🌐 Step 5: Test Connection

### 5.1 Open Neo4j Browser
1. Click the **"Open"** dropdown on your database
2. Select **"Neo4j Browser"**
3. A browser window will open at `http://localhost:7474`

### 5.2 Login
1. **Connect URL:** `neo4j://localhost:7687` (should be pre-filled)
2. **Username:** `neo4j`
3. **Password:** `spacebiology123`
4. Click **"Connect"**

### 5.3 Run Test Query
In the Neo4j Browser command line (top of page), type:
```cypher
MATCH (n) RETURN count(n) as node_count
```
Press **Enter** or click the **▶ Run** button.

**Expected Result:** `node_count: 0` (empty database, ready for data!)

---

## ✅ Step 6: Verify Configuration

### 6.1 Run Verification Script
Open PowerShell in your ASTROBIOMERS backend folder and run:

```powershell
cd c:\Users\mi\Downloads\ASTROBIOMERS\backend
python verify_neo4j.py
```

This script will:
- ✅ Check Neo4j connectivity
- ✅ Verify credentials
- ✅ Test database access
- ✅ Confirm pipeline can connect

### 6.2 Expected Output
```
🔍 Testing Neo4j Connection...
✓ Connected to Neo4j at bolt://localhost:7687
✓ Database 'astrobiomers' is accessible
✓ Successfully ran test query
✓ Configuration is correct!

🎉 Neo4j is ready for knowledge graph loading!
```

---

## 🚀 Step 7: Load Your Knowledge Graph

### 7.1 Run Pipeline with Neo4j Loading
```powershell
cd c:\Users\mi\Downloads\ASTROBIOMERS\backend
python -m knowledge_graph.cli build --papers 50 --load-neo4j
```

### 7.2 What This Does
- Loads your 50 processed papers
- Creates **Entity nodes** (Stressor, Phenotype)
- Creates **Relationship edges** between entities
- Links entities to **Paper nodes** with provenance
- Builds complete knowledge graph structure

**Processing Time:** ~15-30 seconds

### 7.3 Expected Output
```
✓ Stage 1-7: Complete (from previous run - will skip)
✓ Stage 8: Neo4j Loading
   - Created 25 entity nodes
   - Created 5 relationship edges
   - Created 50 paper nodes
   - Total nodes: 75
   - Total relationships: 55+

🎉 Knowledge graph loaded successfully!
```

---

## 🔍 Step 8: Explore Your Knowledge Graph

### 8.1 Open Neo4j Browser
- Should already be open from Step 5
- Or click **"Open" → "Neo4j Browser"** in Neo4j Desktop

### 8.2 Run Exploration Queries

**See All Entities:**
```cypher
MATCH (n)
RETURN n
LIMIT 25
```

**Find Stressors:**
```cypher
MATCH (s:Stressor)
RETURN s.name as stressor, s.count as mentions
ORDER BY s.count DESC
```

**Discover Relationships:**
```cypher
MATCH (s:Stressor)-[r:AFFECTS|CAUSES|INDUCES]->(p:Phenotype)
RETURN s.name as stressor, type(r) as relationship, p.name as phenotype, r.confidence
ORDER BY r.confidence DESC
```

**Find Papers About Microgravity:**
```cypher
MATCH (p:Paper)-[:MENTIONS]->(e:Entity {name: "microgravity"})
RETURN p.title, p.pmcid, p.year
ORDER BY p.year DESC
```

**Graph Visualization:**
```cypher
MATCH path = (s:Stressor)-[r]->(p:Phenotype)
RETURN path
LIMIT 10
```

### 8.3 Interact with Graph
- **Click nodes** to see properties
- **Click edges** to see relationship details
- **Drag nodes** to rearrange visualization
- **Double-click** to expand connections
- Use **controls** at bottom to zoom/pan

---

## 🛠️ Troubleshooting

### Issue: "Connection Refused"
**Solution:**
1. Check Neo4j Desktop shows **"Active"** status
2. Wait 30 seconds after starting
3. Restart database: Stop → Wait 5 sec → Start

### Issue: "Authentication Failed"
**Solution:**
1. Verify password is `spacebiology123`
2. Or change `.env` file to match your password
3. Restart verification script

### Issue: "Database 'astrobiomers' not found"
**Solution:**
1. In Neo4j Desktop, click database settings (•••)
2. Go to "Settings" tab
3. Verify name is exactly `astrobiomers`
4. Or use default `neo4j` database name in `.env`

### Issue: Neo4j Desktop Won't Start
**Solution:**
1. Close Neo4j Desktop completely
2. Restart as Administrator (right-click → Run as Administrator)
3. Try starting database again

---

## 📚 Next Steps After Setup

### Immediate Actions:
1. ✅ Complete Neo4j Desktop installation (Steps 1-2)
2. ✅ Create and start database (Steps 3-4)
3. ✅ Verify connection (Steps 5-6)
4. ✅ Load knowledge graph (Step 7)
5. ✅ Explore data (Step 8)

### Then Proceed To:
- 📊 **Scale pipeline:** Process all 607 papers
- 🎨 **Frontend development:** Build React visualization UI
- 🔬 **Advanced analytics:** PageRank, community detection
- 🌐 **API integration:** Connect FastAPI to Neo4j
- 🚀 **Production deployment:** AuraDB cloud migration

---

## 📞 Quick Reference

### Connection Details
```
URI:      bolt://localhost:7687
Username: neo4j
Password: spacebiology123
Database: astrobiomers
Browser:  http://localhost:7474
```

### Important Commands
```powershell
# Verify connection
python verify_neo4j.py

# Load knowledge graph
python -m knowledge_graph.cli build --papers 50 --load-neo4j

# Check pipeline status
python -m knowledge_graph.cli status

# Start backend API
uvicorn main:app --reload
```

### Key Files
- `.env` - Configuration file (credentials)
- `verify_neo4j.py` - Connection test script
- `data/pipeline_output/` - Generated data files

---

## ⏱️ Time Estimates

| Task | Duration |
|------|----------|
| Download Neo4j Desktop | 2-5 min |
| Install Neo4j Desktop | 2-3 min |
| Create & start database | 1-2 min |
| Verify connection | 1 min |
| Load knowledge graph | 1 min |
| **TOTAL** | **~10-15 min** |

---

## 🎯 Success Criteria

You'll know setup is complete when:
- ✅ Neo4j Desktop shows "Active" green status
- ✅ Neo4j Browser opens at http://localhost:7474
- ✅ `verify_neo4j.py` shows all checks passing
- ✅ Knowledge graph loading completes successfully
- ✅ Can run Cypher queries and see results

---

## 🎉 Ready to Begin?

**Start with Step 1** and work through each section. The entire process is straightforward and well-documented. Each step builds on the previous one.

**Questions while installing?** Run the verification script at any point to check your progress:
```powershell
python verify_neo4j.py
```

**Let's build your knowledge graph! 🚀**
