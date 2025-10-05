# ⚡ QUICK REFERENCE - Frontend Commands

## 🚀 Getting Started (First Time)

```powershell
# 1. Install dependencies
cd frontend
npm install --legacy-peer-deps

# 2. Create environment file
cp .env.example .env

# 3. Start development server
npm run dev

# 4. Open browser
# Navigate to http://localhost:3000
```

**Expected time:** 5 minutes total

---

## 📋 Daily Commands

```powershell
# Start development server
npm run dev

# Run with type checking
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

---

## 🎨 Component Usage

### Button
```tsx
import Button from '@/components/ui/Button'

<Button variant="primary" size="md">Click Me</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button isLoading>Loading...</Button>
```

### Card
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

<Card hover>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content
  </CardContent>
</Card>
```

### StatCard
```tsx
import StatCard from '@/components/ui/StatCard'

<StatCard
  title="Total Papers"
  value={106}
  icon="📄"
  trend="+12%"
/>
```

---

## 🔌 API Hooks

```tsx
import {
  useGraphData,
  useCytoscapeGraph,
  useStatistics,
  useStressors,
  usePhenotypes,
  useEntitySearch,
  useNodeDetails,
} from '@/hooks/useKnowledgeGraph'

// In component:
const { data, isLoading, error } = useStatistics()
const { data: graph } = useCytoscapeGraph()
const { data: results } = useEntitySearch(query)
```

---

## 🎯 State Management

### UI Store
```tsx
import { useUIStore } from '@/stores'

const {
  selectedNodeId,
  setSelectedNodeId,
  theme,
  setTheme,
  viewMode,
  setViewMode,
} = useUIStore()
```

### Filter Store
```tsx
import { useFilterStore } from '@/stores'

const {
  filters,
  setFilters,
  clearFilters,
  toggleEntityType,
} = useFilterStore()
```

### Preferences Store
```tsx
import { usePreferencesStore } from '@/stores'

const { preferences, setPreferences } = usePreferencesStore()
```

---

## 🎨 Design System

### Colors
```tsx
// Primary
className="bg-space-500 text-white"

// Accent
className="bg-accent-500 text-white"

// Semantic
className="bg-success"    // Green
className="bg-warning"    // Amber
className="bg-error"      // Red
```

### Typography
```tsx
className="font-sans"      // Inter - body
className="font-display"   // Space Grotesk - headings
className="font-mono"      // JetBrains Mono - code
```

### Utilities
```tsx
import { cn, formatNumber, getEntityColor } from '@/utils/helpers'

cn('base', condition && 'conditional')  // Class merging
formatNumber(1234567)  // "1,234,567"
getEntityColor('STRESSOR')  // "#ef4444"
```

---

## 🐛 Common Issues

### "Cannot find module '@/components/...'"
**Fix:** Restart TypeScript server (Ctrl+Shift+P → TypeScript: Restart TS Server)

### "fetch failed" or API errors
**Fix:** 
1. Check backend: http://localhost:8000/health
2. Verify `.env` has `VITE_API_URL=http://localhost:8000`

### Tailwind classes not working
**Fix:** `npm install -D @tailwindcss/forms @tailwindcss/typography`

### npm install fails
**Fix:** `npm install --legacy-peer-deps`

---

## 📦 Build & Deploy

```powershell
# Production build
npm run build

# Test production build locally
npm run preview

# Deploy to Vercel
npm install -g vercel
vercel

# Deploy to Netlify
npm install -g netlify-cli
netlify deploy --prod
```

---

## 📁 File Locations

| Need | File Location |
|------|---------------|
| Add component | `src/components/` |
| Add hook | `src/hooks/` |
| Add API method | `src/services/knowledgeGraphAPI.ts` |
| Add type | `src/types/index.ts` |
| Add utility | `src/utils/helpers.ts` |
| Edit colors | `tailwind.config.js` |
| Edit styles | `src/styles/globals.css` |

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend Dev | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Storybook | http://localhost:6006 |

---

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Dependencies & scripts |
| `tsconfig.json` | TypeScript config |
| `vite.config.js` | Vite config (aliases, proxy) |
| `tailwind.config.js` | Design system |
| `.eslintrc.cjs` | Linting rules |
| `.prettierrc` | Code formatting |
| `.env` | Environment variables |

---

## 🎯 Next Features to Add (Phase 2)

1. **AI Research Assistant**
   - File: `src/components/ai-assistant/ChatInterface.tsx`
   - Hook: `src/hooks/useAIAssistant.ts`
   - API: LangChain.js + OpenAI

2. **Inspector Panel**
   - File: `src/components/discovery-hub/InspectorPanel.tsx`
   - Hook: `useNodeDetails(nodeId)`
   - Shows: Entity details, connections, actions

3. **Advanced Graph Controls**
   - Expand/collapse neighborhoods
   - Pathfinding visualization
   - Layout switching
   - Subgraph extraction

4. **Filtering Sidebar**
   - Entity type toggles
   - Date range picker
   - Keyword search
   - Saved filters

---

## 🏆 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search bar |
| `Esc` | Close dropdown/modal |
| `Tab` | Navigate focusable elements |
| `Enter` | Activate button/link |
| `Space` | Toggle checkbox/switch |
| `Ctrl+K` | Command palette (future) |

---

## 📊 Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| First Contentful Paint | <1.5s | Chrome DevTools → Lighthouse |
| Time to Interactive | <3.5s | Chrome DevTools → Lighthouse |
| Bundle Size (gzip) | <400 KB | `npm run build` output |
| Lighthouse Score | ≥90 | Chrome DevTools → Lighthouse |

---

## 🎓 Learn More

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Cytoscape.js](https://js.cytoscape.org/)
- [TanStack Query](https://tanstack.com/query/latest)

---

**Save this file! Pin it to your editor! Use it daily!** 📌
