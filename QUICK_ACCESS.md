# 🎯 Quick Access Guide

## Your NeuroAI Platform is NOW RUNNING! 🚀

---

## 📱 Access URLs

| Service          | URL                           | Status     |
| ---------------- | ----------------------------- | ---------- |
| **Frontend**     | http://localhost:8080         | ✅ Running |
| **Backend API**  | http://localhost:8000/api/v1/ | ✅ Running |
| **Django Admin** | http://localhost:8000/admin/  | ✅ Ready   |

---

## 🧪 Quick Test Commands

### Test Backend is Responding

```bash
curl http://localhost:8000/api/v1/system/
```

**Expected**: JSON response with platform info

### Test Frontend is Loading

```bash
curl http://localhost:8080/ | head -20
```

**Expected**: HTML response with React app

### Test API Connection

```bash
# Get drugs (currently empty)
curl http://localhost:8000/api/v1/drugs/

# Get targets
curl http://localhost:8000/api/v1/targets/

# Get pathways
curl http://localhost:8000/api/v1/pathways/
```

---

## 📊 Test ML Predictions

### Binding Affinity Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predictions/binding-affinity/ \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_smiles": "CCO",
    "target_name": "TNF-alpha"
  }'
```

### Toxicity Assessment

```bash
curl -X POST http://localhost:8000/api/v1/predictions/toxicity/ \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_smiles": "CCO",
    "molecule_name": "Ethanol"
  }'
```

### Molecule Analysis

```bash
curl -X POST http://localhost:8000/api/v1/predictions/molecule-analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_smiles": "CCO"
  }'
```

---

## 🖥️ System Status

### Check Services Running

```bash
ps aux | grep -E "(manage.py runserver|npm run dev)" | grep -v grep
```

### View Live Logs

```bash
# Backend logs (real-time)
tail -f /tmp/backend.log

# Frontend logs (real-time)
tail -f /tmp/frontend.log

# Both logs together
tail -f /tmp/backend.log /tmp/frontend.log
```

---

## 🛑 Stop Services

### Kill All Services

```bash
# Method 1: Kill by port
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Method 2: Kill by process name
pkill -f "manage.py runserver"
pkill -f "npm run dev"
```

---

## 🔄 Restart Services

### Restart Backend Only

```bash
pkill -f "manage.py runserver"
sleep 2
cd /home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/backend && \
  python manage.py runserver 0.0.0.0:8000 &
```

### Restart Frontend Only

```bash
pkill -f "npm run dev"
sleep 2
cd /home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/pathfinder-neurals && \
  npm run dev &
```

### Restart Everything

```bash
/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/startup.sh
```

---

## 📁 Important Folders

```
/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/
├── backend/                    ← Django REST API source
├── pathfinder-neurals/         ← React frontend source
├── android/                    ← Kotlin Android app
├── PROJECT_RUNNING_STATUS.md   ← Full status report (YOU ARE HERE)
├── LOVABLE_PROMPT.md           ← Frontend generation prompt
├── FRONTEND_SETUP_GUIDE.md     ← Frontend setup instructions
├── TECHNICAL_DOCUMENTATION.md  ← Technical architecture
└── START_HERE.md               ← Getting started guide
```

---

## 🐛 Troubleshooting

### Frontend won't load?

1. Check if running: `ps aux | grep npm | grep -v grep`
2. Check logs: `tail -50 /tmp/frontend.log`
3. Try restarting: `pkill -f "npm run dev"` then restart

### Backend API not responding?

1. Check if running: `ps aux | grep manage.py | grep -v grep`
2. Check logs: `tail -50 /tmp/backend.log`
3. Test curl: `curl http://localhost:8000/api/v1/system/`
4. Try restarting: `pkill -f "manage.py runserver"` then restart

### Port already in use?

```bash
# Find what's using the port
lsof -i :8000      # For backend
lsof -i :8080      # For frontend

# Kill the process
kill -9 <PID>
```

### ML Models slow on first request?

- **Normal!** First prediction takes 10-15 seconds (models load)
- **After first load**: 2-5 seconds per prediction
- This only happens once per service restart

---

## ✨ Features Available

### Frontend Features

- ✅ Drug browser with search and filters
- ✅ Target explorer with disease relevance
- ✅ Pathway visualization and analysis
- ✅ Binding affinity prediction tool
- ✅ Toxicity assessment tool
- ✅ Drug response prediction
- ✅ Disease progression simulation
- ✅ Responsive mobile design

### Backend Features

- ✅ RESTful API with 15+ endpoints
- ✅ Django admin panel for data management
- ✅ ML model inference (GraphDTA, MedGemma, ESM-2, RDKit)
- ✅ Disease trajectory modeling
- ✅ Drug-target interaction mapping
- ✅ Pathway effects calculation
- ✅ CORS support for frontend

### ML Models Ready

- ✅ **GraphDTA** - Binding affinity prediction
- ✅ **MedGemma-7B** - Toxicity and medical reasoning
- ✅ **ESM-2-33M** - Protein embeddings
- ✅ **RDKit** - Molecular analysis

---

## 🎓 Learning Resources

| Resource               | Location                                                 |
| ---------------------- | -------------------------------------------------------- |
| Complete API Reference | [LOVABLE_PROMPT.md](LOVABLE_PROMPT.md)                   |
| Frontend Setup Guide   | [FRONTEND_SETUP_GUIDE.md](FRONTEND_SETUP_GUIDE.md)       |
| Technical Architecture | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) |
| Getting Started        | [START_HERE.md](START_HERE.md)                           |
| Complete Status Report | [PROJECT_RUNNING_STATUS.md](PROJECT_RUNNING_STATUS.md)   |
| Full Project Index     | [FRONTEND_INDEX.md](FRONTEND_INDEX.md)                   |

---

## 🎯 Next Steps

1. **Open Frontend**: http://localhost:8080
2. **Test an API endpoint**: `curl http://localhost:8000/api/v1/system/`
3. **Try a prediction**: Use the curl commands above
4. **Check logs**: `tail -f /tmp/backend.log`
5. **Load sample data**: `cd backend && python manage.py seed_sample_data`
6. **Create admin user**: `cd backend && python manage.py createsuperuser`

---

## 📞 Need Help?

- Check logs: `/tmp/backend.log` or `/tmp/frontend.log`
- Read documentation: See Learning Resources above
- Common issues: See Troubleshooting section
- API errors: Check the error message in response

---

## 🎉 Summary

```
✅ Backend: Running on http://localhost:8000
✅ Frontend: Running on http://localhost:8080
✅ ML Models: Ready (loaded on-demand)
✅ Database: Initialized and ready
✅ API: All endpoints operational
✅ Development: Full HMR support enabled

You're ready to start using NeuroAI! 🚀
```

**Enjoy your AI-powered drug discovery platform!**
