# Troubleshooting Guide - Groww Mutual Fund FAQ Assistant

## Common Issues and Solutions

### Issue 1: "Oh no. Error running app"

**Symptoms**: Streamlit shows error page with sad emoji

**Solutions**:

1. **Check Python version** (requires Python 3.8+):
   ```bash
   python --version
   ```

2. **Verify virtual environment is activated**:
   - Windows: `venv\Scripts\activate.bat`
   - macOS/Linux: `source venv/bin/activate`

3. **Reinstall dependencies**:
   ```bash
   pip install --upgrade -r phases/phase-0-foundation/requirements.txt
   ```

4. **Check .env file exists**:
   ```bash
   # Windows
   if exist "phases\phase-0-foundation\.env" echo .env found
   
   # macOS/Linux
   ls -la phases/phase-0-foundation/.env
   ```

5. **Verify API keys are configured**:
   ```bash
   python test_streamlit_setup.py
   ```

---

### Issue 2: "ModuleNotFoundError: No module named 'src'"

**Symptoms**: Import error when starting the app

**Solutions**:

1. **Ensure __init__.py files exist**:
   ```bash
   # These files should exist:
   # - phases/phase-0-foundation/__init__.py
   # - phases/phase-1-collection/src/__init__.py
   # - phases/phase-2-processing/src/__init__.py
   # - phases/phase-3-retrieval/src/__init__.py
   # - phases/phase-4-orchestration/src/__init__.py
   # - phases/phase-5-frontend/__init__.py
   ```

2. **Recreate missing __init__.py files**:
   ```bash
   python -c "
   from pathlib import Path
   for path in [
       'phases/phase-0-foundation/__init__.py',
       'phases/phase-1-collection/src/__init__.py',
       'phases/phase-2-processing/src/__init__.py',
       'phases/phase-3-retrieval/src/__init__.py',
       'phases/phase-4-orchestration/src/__init__.py',
       'phases/phase-5-frontend/__init__.py',
   ]:
       Path(path).touch()
   print('Created all __init__.py files')
   "
   ```

---

### Issue 3: "LangChain/Gemini API Error"

**Symptoms**: Error about API keys or quota exceeded

**Solutions**:

1. **Verify API keys in .env**:
   ```bash
   cat phases/phase-0-foundation/.env
   ```

2. **Check API key format**:
   - Gemini keys should start with `AIzaSy`
   - Groq keys should start with `gsk_`

3. **Test API connectivity**:
   ```bash
   python -c "
   import os
   from dotenv import load_dotenv
   from pathlib import Path
   
   load_dotenv(Path('phases/phase-0-foundation/.env'))
   
   gemini_key = os.getenv('GEMINI_API_KEY_1')
   print(f'Gemini Key 1: {gemini_key[:20]}...' if gemini_key else 'Not found')
   "
   ```

4. **Rotate API keys manually**:
   - The system automatically cycles through 3 Gemini keys
   - If all are exhausted, it falls back to Groq
   - Check your API quota at: https://console.cloud.google.com/

---

### Issue 4: "Chroma Database Error"

**Symptoms**: Error about vector database or embeddings

**Solutions**:

1. **Verify Chroma directory exists**:
   ```bash
   # Windows
   if exist "chroma" echo Chroma directory found
   
   # macOS/Linux
   ls -la chroma/
   ```

2. **Clear and reinitialize Chroma**:
   ```bash
   python phases/phase-2-processing/clear_chroma.py
   python -c "from src.ingest import ingest_daily; ingest_daily()"
   ```

3. **Check disk space**:
   - Chroma database requires ~100MB
   - Ensure you have sufficient disk space

---

### Issue 5: "Scheduler/Background Job Error"

**Symptoms**: Error about APScheduler or background tasks

**Solutions**:

1. **Verify APScheduler is installed**:
   ```bash
   pip show apscheduler
   ```

2. **Check scheduler logs**:
   - The scheduler runs daily at 10 AM IST
   - Check `phases/phase-4-orchestration/src/scheduler.py` for logging

3. **Manually trigger pipeline**:
   ```bash
   python -c "
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path('phases/phase-4-orchestration')))
   from src.scheduler import run_pipeline_once
   run_pipeline_once()
   print('Pipeline executed')
   "
   ```

---

### Issue 6: "Port 8501 Already in Use"

**Symptoms**: "Address already in use" error

**Solutions**:

1. **Kill existing Streamlit process**:
   ```bash
   # Windows
   netstat -ano | findstr :8501
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -i :8501
   kill -9 <PID>
   ```

2. **Use different port**:
   ```bash
   streamlit run phases/phase-5-frontend/app.py --server.port 8502
   ```

---

### Issue 7: "Encoding Error in app.py"

**Symptoms**: "charmap codec can't decode byte" error

**Solutions**:

1. **Ensure UTF-8 encoding**:
   - The app.py file uses UTF-8 encoding
   - If you edited it, save with UTF-8 encoding

2. **Verify file encoding**:
   ```bash
   python -c "
   with open('phases/phase-5-frontend/app.py', 'r', encoding='utf-8') as f:
       content = f.read()
   print('✓ File is valid UTF-8')
   "
   ```

---

## Diagnostic Commands

### Run Full Setup Test
```bash
python test_streamlit_setup.py
```

### Test RAG Engine
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('phases/phase-3-retrieval')))
from src import rag_engine

# Test validate_query
is_allowed, reason = rag_engine.validate_query('What is the NAV of Groww Liquid Fund?')
print(f'Query validation: allowed={is_allowed}')

# Test answer
response = rag_engine.answer('What is the NAV of Groww Liquid Fund?')
print(f'Answer: {response[\"answer\"][:100]}...')
"
```

### Test Imports
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('phases/phase-3-retrieval')))
sys.path.insert(0, str(Path('phases/phase-4-orchestration')))

from src import rag_engine
from src.shared import SCOPE_FUNDS
from src.scheduler import start_scheduler_once

print('✓ All imports successful')
print(f'  - RAG Engine: OK')
print(f'  - Shared module: OK ({len(SCOPE_FUNDS)} funds)')
print(f'  - Scheduler: OK')
"
```

### Check Environment
```bash
python -c "
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('phases/phase-0-foundation/.env'))

print('Environment Variables:')
print(f'  - GEMINI_API_KEY_1: {\"✓\" if os.getenv(\"GEMINI_API_KEY_1\") else \"✗\"}')
print(f'  - GEMINI_API_KEY_2: {\"✓\" if os.getenv(\"GEMINI_API_KEY_2\") else \"✗\"}')
print(f'  - GEMINI_API_KEY_3: {\"✓\" if os.getenv(\"GEMINI_API_KEY_3\") else \"✗\"}')
print(f'  - GROQ_API_KEY: {\"✓\" if os.getenv(\"GROQ_API_KEY\") else \"✗\"}')
"
```

---

## Getting Help

If you encounter an issue not listed here:

1. **Check the logs**:
   - Streamlit logs appear in the terminal
   - Look for error messages and stack traces

2. **Run diagnostic tests**:
   ```bash
   python test_streamlit_setup.py
   ```

3. **Check GitHub Issues**:
   - https://github.com/Jagrati-hub/MutualFund_ChatBot_Milestone2/issues

4. **Review documentation**:
   - `READY_TO_RUN.md` - Quick start guide
   - `LOCAL_SETUP_GUIDE.md` - Detailed setup instructions
   - `phases/docs/` - Architecture and implementation details

---

## Performance Tips

1. **First load may be slow** (30-60 seconds):
   - Streamlit is initializing the RAG engine
   - Chroma is loading embeddings
   - This is normal

2. **Subsequent queries are faster** (5-10 seconds):
   - Embeddings are cached
   - API calls are optimized

3. **To speed up development**:
   - Use `streamlit run --logger.level=error` to reduce logging
   - Use `--client.showErrorDetails=false` to hide verbose errors

---

## Still Having Issues?

1. **Verify all files exist**:
   ```bash
   python -c "
   from pathlib import Path
   required_files = [
       'phases/phase-0-foundation/.env',
       'phases/phase-0-foundation/requirements.txt',
       'phases/phase-0-foundation/system_prompt.md',
       'phases/phase-3-retrieval/src/rag_engine.py',
       'phases/phase-5-frontend/app.py',
   ]
   for f in required_files:
       status = '✓' if Path(f).exists() else '✗'
       print(f'{status} {f}')
   "
   ```

2. **Check Python path**:
   ```bash
   python -c "import sys; print('\\n'.join(sys.path))"
   ```

3. **Verify dependencies**:
   ```bash
   pip list | grep -E 'streamlit|langchain|chromadb|apscheduler'
   ```

---

## Quick Recovery

If everything is broken, try a clean restart:

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove virtual environment
rm -rf venv  # or rmdir /s venv on Windows

# 3. Run setup script
run_local.bat  # Windows
./run_local.sh  # macOS/Linux

# 4. If still broken, clear cache
rm -rf .cache
rm -rf chroma
python phases/phase-2-processing/clear_chroma.py
```

Then try running the app again.
