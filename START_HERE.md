# 🚀 START HERE - NeuroAI Frontend with Lovable

## What You Need to Do (3 Simple Steps)

### Step 1: Start Your Backend (30 seconds)

```bash
cd /home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/backend
python manage.py runserver
```

✅ You should see: "Starting development server at http://127.0.0.1:8000/"

### Step 2: Copy Your Lovable Prompt (2 minutes)

You have TWO options:

**Option A: Quick & Simple** (Recommended for first-timers)

```
Go to: /home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/LOVABLE_QUICK_PROMPT.txt
Copy entire file contents
```

**Option B: Detailed & Complete** (For more control)

```
Go to: /home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/LOVABLE_PROMPT.md
Copy entire file contents
```

### Step 3: Generate Frontend with Lovable (5 minutes)

1. Open: https://lovable.dev
2. Click "Create New Project" or start a chat
3. Paste your copied prompt
4. Click Send and wait for generation
5. Download the generated project

---

## Step 4: Set Up Generated Frontend (5 minutes)

```bash
# Navigate to generated project
cd /path/to/generated/neuroai-frontend

# Create environment file
cat > .env << 'EOF'
REACT_APP_API_BASE_URL=http://localhost:8000
EOF

# Install and start
npm install
npm start
```

✅ Your frontend will open at: http://localhost:3000

---

## Done! ✨

You now have:

- ✅ Backend API running at: `http://localhost:8000/api/v1/`
- ✅ Frontend running at: `http://localhost:3000`
- ✅ Full drug discovery platform ready to explore!

---

## What Each Generated Component Does

### 🔬 Drug Browser

- Browse all 150+ drugs in database
- Filter by CNS viability and approval status
- Search by name or drug ID

### 👁️ Target Explorer

- Look at biological targets (genes/proteins)
- See disease relevance scores
- Find toxicity warnings

### 🛤️ Pathway Viewer

- Explore disease-relevant biological pathways
- See how drugs affect pathways
- Visualize pathway categories (neuroinflammation, Alzheimer's, etc.)

### 🧬 Prediction Tools

- **Binding Affinity**: Predict drug-target binding strength
- **Toxicity Assessment**: Evaluate molecular toxicity
- **Drug Response**: Comprehensive multi-model prediction

### ⚡ Simulation Dashboard

- Run disease progression simulations
- Compare no-drug vs. with-drug scenarios
- See trajectory differences

---

## API Endpoints Your Frontend Uses

All these endpoints will be called automatically:

```
GET  /api/v1/drugs/              → List all drugs
GET  /api/v1/drugs/{id}/         → Get drug details
GET  /api/v1/targets/            → List all targets
GET  /api/v1/pathways/           → List all pathways
GET  /api/v1/pathway-effects/    → Drug effects on pathways
POST /api/v1/predictions/...     → Make predictions
POST /api/v1/simulate/           → Run simulations
GET  /api/v1/system/             → System info
```

---

## Troubleshooting

### ❌ "Cannot connect to backend"

```bash
# Make sure backend is running:
curl http://localhost:8000/api/v1/system/

# If you see JSON response, backend is OK!
# Check your .env file has:
REACT_APP_API_BASE_URL=http://localhost:8000
```

### ❌ "Port 3000 is already in use"

```bash
# Change port:
PORT=3001 npm start
```

### ❌ "Predictions very slow"

Normal! First prediction takes 10-15 seconds (ML models loading).  
Subsequent predictions are 2-5 seconds.  
**Tip**: Add loading indicator that says "Initializing ML models..."

---

## File Locations

| What               | Where                                                                      |
| ------------------ | -------------------------------------------------------------------------- |
| Backend            | `/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/backend/`                 |
| Quick Prompt       | `/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/LOVABLE_QUICK_PROMPT.txt` |
| Detailed Prompt    | `/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/LOVABLE_PROMPT.md`        |
| Setup Guide        | `/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/FRONTEND_SETUP_GUIDE.md`  |
| Full Index         | `/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/FRONTEND_INDEX.md`        |
| Generated Frontend | Wherever you download it from Lovable                                      |

---

## Important Reminders ⚠️

Your frontend MUST display these disclaimers prominently:

> - "This is exploratory AI, NOT a clinical tool"
> - "Results should be reviewed by domain experts"
> - "No diagnostic or treatment recommendations"

Show these on:

- Every prediction result page
- Simulation comparison page
- Drug detail pages with warnings

---

## Performance Tips

| Issue             | Solution                                           |
| ----------------- | -------------------------------------------------- |
| Slow drug search  | Add a 300ms debounce to search input               |
| Slow simulations  | Show loading indicator, set timeout to 30+ seconds |
| Pagination slow   | Fetch smarter: only fetch current page             |
| UI feels sluggish | Use React.memo on expensive components             |

---

## Next: Choose Your Prompt to Use

### Use LOVABLE_QUICK_PROMPT.txt if:

- ✅ First time using Lovable
- ✅ Want to get frontend running in 5 minutes
- ✅ Happy with standard implementation
- ✅ Can customize later if needed

**→ START WITH THIS ONE**

### Use LOVABLE_PROMPT.md if:

- ✅ Want detailed specifications
- ✅ Plan significant customization
- ✅ Need full API documentation
- ✅ Have specific design requirements

---

## You're All Set! 🎉

```
👉 Next: Copy your chosen prompt to Lovable
👉 Wait: Let Lovable generate your frontend (2-5 minutes)
👉 Run: npm install && npm start
👉 Enjoy: Your AI drug discovery platform!
```

**Questions?** Check [FRONTEND_INDEX.md](./FRONTEND_INDEX.md) for full navigation guide.

---

**Status**: Backend + Frontend generation ready ✅  
**Time to working app**: ~15 minutes  
**Generated by**: NeuroAI Team  
**Date**: February 25, 2026
