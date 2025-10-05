# 🔧 Knowledge Graph Fix Applied

## Issue Identified:
The DEMO filter was too aggressive - it was checking `n.id STARTS WITH 'DEMO'` but when `n.id` was NULL, the entire WHERE clause would fail, filtering out legitimate nodes.

## Fix Applied:
Changed the query to check for NULL first:
```cypher
WHERE NOT (
    (n.id IS NOT NULL AND n.id STARTS WITH 'DEMO') OR 
    (n.pmid IS NOT NULL AND n.pmid STARTS WITH 'DEMO')
)
```

This ensures:
- If `n.id` is NULL, it won't try to check `STARTS WITH`
- Only checks DEMO prefix if the property exists
- Allows all other nodes through

## Status:
✅ Backend restarted with fix (Process 22148)
✅ Frontend still running on localhost:8080
✅ Ready to test

## Test Now:
1. Refresh your browser: http://localhost:8080/knowledge-graph
2. Search for: "stem cell" (or "stem cells")
3. You should now see nodes appearing in the graph

## What to Expect:
- Green circles = Papers (about stem cells)
- Blue/Purple circles = Entities (organisms, compounds, etc.)
- Lines = Relationships between them
- Should see ~10-20 nodes minimum

**Fixed:** October 5, 2025, 23:02
