# ⚡ Quick Start: Your Neo4j Database

**Status:** Neo4j Desktop is RUNNING ✅  
**Issue:** Database needs to be started 🔴

---

## 🎯 What You Need to Do (30 seconds)

### Open Neo4j Desktop
1. **Find Neo4j Desktop** in your taskbar or start menu
2. **Click on it** to bring it to the front

### Start Your Database
Look for your database in the Neo4j Desktop interface:

#### Option A: If you see a database called "astrobiomers"
1. Find the database named **"astrobiomers"**
2. Click the **"Start"** button (blue/green button on the right)
3. Wait for status to show **"Active"** (green circle)
4. **Done!** - Come back here

#### Option B: If you see any other database (like "neo4j" or "graph.db")
1. Find any database in your projects
2. Click the **"Start"** button
3. Note the database name (you'll see it at the top)
4. Come back here - I'll update the configuration

#### Option C: If you don't see any databases
1. Click **"+ New"** button (near Projects)
2. Click **"+ Add"** → **"Local DBMS"**
3. Configure:
   - **Name:** astrobiomers
   - **Password:** spacebiology123
   - **Version:** 5.x (latest)
4. Click **"Create"**
5. Click **"Start"**
6. Come back here

---

## ✅ How to Know It's Working

In Neo4j Desktop, you should see:
- ✅ **Green circle** next to your database
- ✅ Status shows **"Active"** or **"Running"**
- ✅ **"Start"** button changes to **"Stop"**

---

## 🚀 Once Started, Run This Command

After starting your database in Neo4j Desktop, run:

```powershell
cd c:\Users\mi\Downloads\ASTROBIOMERS\backend
python verify_neo4j.py
```

**If it works, you'll see:**
```
✓ Connected to Neo4j at bolt://localhost:7687
✓ Database 'astrobiomers' is accessible
✓ Successfully executed query
🎉 All tests passed!
```

**Then immediately run:**
```powershell
python -m knowledge_graph.cli build --papers 50 --load-neo4j
```

This will load your 25 entities and 5 relationships into Neo4j!

---

## 🆘 If You Need Different Credentials

If your database has a different name or password, let me know and I'll update the `.env` file.

**Just tell me:**
- Database name: ___________
- Password: ___________

---

## 📸 Visual Guide

### What Neo4j Desktop Looks Like:

```
┌─────────────────────────────────────────────┐
│  Neo4j Desktop                          _ □ ×│
├─────────────────────────────────────────────┤
│ Projects          │                          │
│ ► My Project     │  Database: astrobiomers  │
│   └─ astrobiomers│  Status: ⚫ Stopped      │
│                   │                          │
│                   │  [▶ Start]  [⚙ Settings]│
└─────────────────────────────────────────────┘
                        ↑
                  CLICK HERE!
```

After clicking Start:

```
┌─────────────────────────────────────────────┐
│  Neo4j Desktop                          _ □ ×│
├─────────────────────────────────────────────┤
│ Projects          │                          │
│ ► My Project     │  Database: astrobiomers  │
│   └─ astrobiomers│  Status: 🟢 Active      │
│                   │                          │
│                   │  [⏹ Stop]  [Open ▼]     │
└─────────────────────────────────────────────┘
                        ↑
                   READY! ✓
```

---

## ⚡ Super Quick Summary

1. **Open Neo4j Desktop** (already running)
2. **Click "Start"** on your database
3. **Wait for green "Active"** status
4. **Run** `python verify_neo4j.py`
5. **Then run** `python -m knowledge_graph.cli build --papers 50 --load-neo4j`

**Total time:** 1 minute!

---

**Ready? Start your database and let me know! 🚀**
