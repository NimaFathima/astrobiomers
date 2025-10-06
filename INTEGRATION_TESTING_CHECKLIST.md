# 🧪 Integration Testing Checklist - Phase 2 Features

## Overview
All Phase 2 features have been integrated into the application. This checklist will guide you through testing each feature systematically.

**Testing Duration**: ~2-3 hours  
**Recommended Browsers**: Chrome (primary), Firefox, Edge

---

## 🚀 Pre-Testing Setup

### 1. Install Dependencies
```bash
cd "C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend"
npm install
```

### 2. Start Backend Server
```bash
cd C:\Users\mi\Downloads\ASTROBIOMERS\backend
python app.py
```
**Expected**: Server starts on `http://localhost:8000`

### 3. Start Frontend Dev Server
```bash
cd "C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend"
npm run dev
```
**Expected**: Dev server starts on `http://localhost:5173`

---

## ✅ Feature Testing Matrix

### Feature 1: Service Worker Registration

**Location**: Automatic on page load  
**Test Time**: 5 minutes

#### Test Steps:
1. ✅ Open browser DevTools (F12)
2. ✅ Go to Application tab → Service Workers
3. ✅ Verify service worker is registered
4. ✅ Check "Offline" checkbox in DevTools
5. ✅ Refresh page - should show offline fallback page
6. ✅ Uncheck "Offline" - should auto-reconnect
7. ✅ Check Application tab → Cache Storage - should see cached assets

**Expected Results**:
- ✅ Service worker status: "Activated and running"
- ✅ Offline fallback page displays with "You're Offline" message
- ✅ Auto-reconnect within 3 seconds when online
- ✅ Cache contains: static-assets-v1, api-cache-v1

**Browser Compatibility**:
- [ ] Chrome - PASS / FAIL
- [ ] Firefox - PASS / FAIL
- [ ] Edge - PASS / FAIL

---

### Feature 2: Voice-Guided Tour

**Location**: Homepage (bottom-right button)  
**Test Time**: 10-15 minutes

#### Test Steps - Full Tour (First Visit):
1. ✅ Open homepage in incognito/private mode
2. ✅ Clear localStorage: `localStorage.clear()` in console
3. ✅ Refresh page
4. ✅ Verify tour starts automatically
5. ✅ Test navigation:
   - [ ] Click "Next" through all 11 steps
   - [ ] Click "Previous" to go back
   - [ ] Click step indicators to jump
6. ✅ Test voice controls:
   - [ ] Hear voice narration for each step
   - [ ] Click pause button - voice stops
   - [ ] Click play - voice resumes
   - [ ] Toggle voice off - no sound
   - [ ] Toggle voice on - sound returns
7. ✅ Verify element highlighting:
   - [ ] Each step highlights correct element
   - [ ] Spotlight effect visible
   - [ ] Pulsing animation works
8. ✅ Complete tour - verify completion modal

#### Test Steps - Quick Tour (Return Visit):
1. ✅ Revisit homepage
2. ✅ Click "Start Tour" button (bottom-right)
3. ✅ Verify quick tour (3 steps) displays
4. ✅ Complete quick tour

**Expected Results**:
- ✅ Tour steps: 11 (first visit), 3 (return visit)
- ✅ Voice narration plays automatically
- ✅ Progress bar updates correctly
- ✅ Step indicators match current step
- ✅ Element highlighting works
- ✅ Tour completion saved to localStorage

**Tour Steps Coverage**:
1. [ ] Welcome - Logo highlighted
2. [ ] Knowledge Graph - Graph section highlighted
3. [ ] Search - Search bar highlighted
4. [ ] Paper Details - Details panel highlighted
5. [ ] AI Assistant - Assistant section highlighted
6. [ ] Entity Extraction - Entities highlighted
7. [ ] Visualization - Graph viz highlighted
8. [ ] Offline Mode - Service worker info
9. [ ] Accessibility - Audio controls highlighted
10. [ ] Data Sources - Sources section highlighted
11. [ ] Completion - Final message

**Browser Compatibility**:
- [ ] Chrome - PASS / FAIL (voices: _______)
- [ ] Firefox - PASS / FAIL (voices: _______)
- [ ] Edge - PASS / FAIL (voices: _______)

---

### Feature 3: Text-to-Speech (AI Assistant)

**Location**: AI Assistant page - Read Aloud buttons  
**Test Time**: 10 minutes

#### Test Steps:
1. ✅ Navigate to `/ai-assistant`
2. ✅ Ask question: "What are the effects of microgravity on bone density?"
3. ✅ Wait for response
4. ✅ Click Volume icon (Read Aloud button)
5. ✅ Verify voice reads response
6. ✅ Click VolumeX icon - stops reading
7. ✅ Click Volume icon again - restarts
8. ✅ Ask another question while speaking
9. ✅ Verify previous speech stops

**Expected Results**:
- ✅ Read Aloud button appears on all assistant messages
- ✅ Voice reads entire message
- ✅ Button toggles between Volume2 and VolumeX icons
- ✅ Only one message speaks at a time
- ✅ Speech rate: 1.0x (natural speed)

**Test Different Voices** (Chrome):
```javascript
// In DevTools console:
speechSynthesis.getVoices().forEach((v, i) => console.log(i, v.name, v.lang));
```

**Browser Compatibility**:
- [ ] Chrome - PASS / FAIL
- [ ] Firefox - PASS / FAIL
- [ ] Edge - PASS / FAIL

---

### Feature 4: Sonification System

**Location**: Knowledge Graph page - Audio Stats button  
**Test Time**: 15 minutes

#### Test Steps - Graph Statistics Sonification:
1. ✅ Navigate to `/knowledge-graph`
2. ✅ Search for: "stem cells"
3. ✅ Wait for graph to load
4. ✅ Locate "Listen to Data" button (top-right of graph)
5. ✅ Click button
6. ✅ Hear voice description + tones
7. ✅ Verify tones for:
   - [ ] Paper count (low frequency)
   - [ ] Entity count (mid frequency)
   - [ ] Relationship count (high frequency)
8. ✅ Click volume toggle - disables audio
9. ✅ Click again - enables audio

#### Test Steps - Data Sonification:
```javascript
// Test in DevTools console:
import { sonifyBarChart, sonifyTrend } from '@/utils/sonification';

// Test bar chart sonification
sonifyBarChart([
  { label: 'Papers', value: 45 },
  { label: 'Entities', value: 28 },
  { label: 'Relationships', value: 67 }
]);

// Test trend sonification
sonifyTrend([10, 15, 22, 30, 45], 'Research Publications');
```

#### Test Steps - UI Feedback Sounds:
```javascript
// Test in DevTools console:
import { playSuccess, playError, playNotification } from '@/utils/sonification';

playSuccess();    // Success sound (ascending)
playError();      // Error sound (descending)
playNotification(); // Notification beep
```

**Expected Results**:
- ✅ Voice describes statistics before tones
- ✅ Tones map to data values (higher value = higher frequency)
- ✅ 200ms gap between tones
- ✅ Volume control works
- ✅ Success sound: ascending C-E-G chord
- ✅ Error sound: descending tones
- ✅ Notification: single beep

**Audio Context State**:
```javascript
// Check audio context:
console.log(new AudioContext().state); // Should be "running" after user interaction
```

**Browser Compatibility**:
- [ ] Chrome - PASS / FAIL
- [ ] Firefox - PASS / FAIL
- [ ] Edge - PASS / FAIL

---

### Feature 5: Audio Charts

**Location**: Knowledge Graph page (integrated)  
**Test Time**: 10 minutes

#### Test Steps:
1. ✅ Search for entity in knowledge graph
2. ✅ Verify StatsAudio component appears
3. ✅ Click "Listen to Data" button
4. ✅ Hear statistics sonification
5. ✅ Toggle audio on/off
6. ✅ Test with different searches:
   - [ ] "microgravity" (should have many papers)
   - [ ] "rare protein" (should have few papers)
   - [ ] "bone loss" (moderate papers)

**Expected Results**:
- ✅ Audio button visible in graph header
- ✅ Sonification reflects actual data
- ✅ Volume icon toggles correctly
- ✅ Loading state during playback
- ✅ Auto-play option works (if enabled)

---

### Feature 6: BART/PEGASUS Summarization

**Location**: Backend API endpoint  
**Test Time**: 10 minutes

#### Test Steps - API Testing:
```bash
# Test 1: BART summarization
curl -X GET "http://localhost:8000/api/papers/12345678/summary?model=bart&max_length=150"

# Test 2: PEGASUS summarization
curl -X GET "http://localhost:8000/api/papers/12345678/summary?model=pegasus&max_length=100"

# Test 3: Fallback (extractive)
curl -X GET "http://localhost:8000/api/papers/12345678/summary?model=invalid"
```

**Expected Response Structure**:
```json
{
  "summary": "Concise summary text...",
  "model_used": "facebook/bart-large-cnn",
  "compression_ratio": 0.45,
  "key_points": [
    "Point 1",
    "Point 2",
    "Point 3"
  ],
  "original_length": 500,
  "summary_length": 150
}
```

#### Test Steps - Frontend Integration:
1. ✅ Navigate to Research page
2. ✅ Click on a paper
3. ✅ Look for "Summarize" button
4. ✅ Click button
5. ✅ Verify summary appears
6. ✅ Check model used (BART/PEGASUS)

**Expected Results**:
- ✅ Summary is coherent and concise
- ✅ Key points extracted correctly
- ✅ Compression ratio: 0.3-0.5
- ✅ Fallback to extractive if model unavailable

**Model Loading Time** (First Request):
- BART: ~10-15 seconds (3GB model)
- PEGASUS: ~8-12 seconds (2.3GB model)
- Subsequent requests: <1 second (cached)

---

## 🎯 Integration Testing Scenarios

### Scenario 1: Complete User Journey
**Duration**: 15 minutes

1. ✅ User visits homepage (first time)
2. ✅ Automatic tour starts
3. ✅ Complete full tour (11 steps)
4. ✅ Navigate to Knowledge Graph
5. ✅ Search for "bone loss"
6. ✅ Listen to graph statistics
7. ✅ Navigate to AI Assistant
8. ✅ Ask question about bone loss
9. ✅ Use Read Aloud feature
10. ✅ Go offline (DevTools)
11. ✅ Verify offline mode works
12. ✅ Go back online
13. ✅ Return to homepage
14. ✅ Start quick tour (3 steps)

**Success Criteria**:
- [ ] All features work seamlessly
- [ ] No console errors
- [ ] Performance remains good
- [ ] User experience is smooth

---

### Scenario 2: Accessibility Testing
**Duration**: 20 minutes

#### Keyboard Navigation:
1. ✅ Tab through entire homepage
2. ✅ Verify all interactive elements focusable
3. ✅ Test tour controls with keyboard:
   - [ ] Enter to activate buttons
   - [ ] Arrow keys for navigation
   - [ ] Escape to close
4. ✅ Test AI Assistant with keyboard
5. ✅ Test Knowledge Graph with keyboard

#### Screen Reader Testing (NVDA/JAWS):
1. ✅ Enable screen reader
2. ✅ Navigate through tour
3. ✅ Verify aria-labels read correctly
4. ✅ Test audio controls
5. ✅ Verify all content accessible

**Success Criteria**:
- [ ] All elements keyboard-accessible
- [ ] Focus indicators visible
- [ ] Screen reader announces all content
- [ ] No keyboard traps

---

### Scenario 3: Browser Compatibility
**Duration**: 30 minutes

Test all features in:
- [ ] Chrome 120+ ✅
- [ ] Firefox 120+ ✅
- [ ] Edge 120+ ✅
- [ ] Safari 17+ (macOS only)

**Known Issues**:
- Safari: Web Speech API limited voice selection
- Firefox: Service Worker cache API slightly different
- Edge: Should work identical to Chrome

---

### Scenario 4: Performance Testing
**Duration**: 15 minutes

#### Metrics to Check:
1. ✅ Initial page load: <3 seconds
2. ✅ Service worker activation: <500ms
3. ✅ Tour start: <200ms
4. ✅ Voice synthesis start: <1 second
5. ✅ Sonification playback: <100ms latency
6. ✅ Graph load: <2 seconds

#### Tools:
- Chrome DevTools → Lighthouse
- Performance tab
- Network tab

**Target Scores**:
- Performance: >85
- Accessibility: >90
- Best Practices: >90
- SEO: >85

---

## 🐛 Bug Tracking

### Critical Issues (Block Submission):
| Issue | Location | Severity | Status | Fix |
|-------|----------|----------|--------|-----|
| Example | Homepage | Critical | ⏳ | Description |

### Minor Issues (Nice to Fix):
| Issue | Location | Severity | Status | Fix |
|-------|----------|----------|--------|-----|
| Example | Tour | Minor | ⏳ | Description |

---

## 📊 Test Results Summary

### Overall Status: ⏳ In Progress

| Feature | Chrome | Firefox | Edge | Status |
|---------|--------|---------|------|--------|
| Service Worker | ⏳ | ⏳ | ⏳ | Not Tested |
| Voice Tour | ⏳ | ⏳ | ⏳ | Not Tested |
| Text-to-Speech | ⏳ | ⏳ | ⏳ | Not Tested |
| Sonification | ⏳ | ⏳ | ⏳ | Not Tested |
| Audio Charts | ⏳ | ⏳ | ⏳ | Not Tested |
| BART/PEGASUS | ⏳ | ⏳ | ⏳ | Not Tested |

**Legend**: ✅ Pass | ❌ Fail | ⚠️ Partial | ⏳ Not Tested

---

## 🎬 Video Demonstration Script

Once testing is complete, record a 7-8 minute video:

### Minute 0-1: Introduction
- "Welcome to Astrobiomers - Space Biology Research Engine"
- Quick overview of tech stack
- Mention 85% feature parity achieved

### Minute 1-2: Voice-Guided Tour
- Show tour button
- Start tour
- Navigate through 2-3 steps
- Show voice controls
- Show element highlighting

### Minute 2-3: Knowledge Graph
- Search for "stem cells"
- Show interactive graph
- Click on nodes
- Demonstrate audio statistics

### Minute 3-4: AI Summarization
- Show paper search
- Generate summary with BART
- Show key points extraction
- Demonstrate compression

### Minute 4-5: AI Assistant + TTS
- Ask question about microgravity
- Show AI response with sources
- Click Read Aloud
- Show voice controls

### Minute 5-6: Sonification Demo
- Return to knowledge graph
- Play audio statistics
- Show data-to-audio mapping
- Demonstrate UI feedback sounds

### Minute 6-7: Offline Mode
- Go offline in DevTools
- Show offline fallback page
- Go back online
- Show auto-reconnect

### Minute 7-8: Wrap-up
- Recap all 12 implemented features
- Show performance metrics
- Mention accessibility features
- Call to action

---

## 📝 Testing Notes

### Test Date: _______________
### Tester: _______________
### Environment:
- OS: _______________
- Browser: _______________
- Backend Version: _______________
- Frontend Version: _______________

### Issues Found:

1. **Issue**: _______________________________
   - **Severity**: Critical / High / Medium / Low
   - **Steps to Reproduce**: _______________________________
   - **Expected**: _______________________________
   - **Actual**: _______________________________
   - **Fix**: _______________________________

2. **Issue**: _______________________________
   - **Severity**: Critical / High / Medium / Low
   - **Steps to Reproduce**: _______________________________
   - **Expected**: _______________________________
   - **Actual**: _______________________________
   - **Fix**: _______________________________

---

## ✅ Sign-off

### Testing Complete:
- [ ] All features tested
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Accessibility verified
- [ ] Video recorded
- [ ] Ready for submission

**Tester Signature**: _______________  
**Date**: _______________

---

## 🚀 Next Steps After Testing

1. **Fix Critical Bugs** (if any)
2. **Record Video Demonstration**
3. **Update PROJECT_DESCRIPTION_ACCURATE.md**
4. **Final Commit & Push**
5. **Submit to NASA Space Apps Challenge**

**Good luck! 🚀🔬✨**
