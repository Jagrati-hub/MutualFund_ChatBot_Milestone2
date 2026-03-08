# Streamlit Cloud Deployment Guide

This guide explains how to deploy the Groww Mutual Fund FAQ Assistant to Streamlit Cloud.

## Prerequisites

1. GitHub account with the repository pushed
2. Streamlit Cloud account (free at https://streamlit.io/cloud)
3. API keys for:
   - Gemini (3 keys recommended)
   - Groq (fallback)
   - GitHub (optional)

## Deployment Steps

### Step 1: Push to GitHub

Ensure all code is pushed to your GitHub repository:

```bash
git add -A
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Create Streamlit Cloud App

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Select the branch: `main`
5. Set the main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

After deployment, configure your API keys:

1. In Streamlit Cloud dashboard, click on your app
2. Click the three dots menu → "Settings"
3. Click "Secrets"
4. Add your API keys in the format:

```toml
GEMINI_API_KEY_1 = "your-key-here"
GEMINI_API_KEY_2 = "your-key-here"
GEMINI_API_KEY_3 = "your-key-here"
GROQ_API_KEY = "your-key-here"
GITHUB_API_KEY = "your-key-here"
```

5. Click "Save"

### Step 4: Verify Deployment

1. Wait for the app to redeploy (usually 1-2 minutes)
2. Check the app URL in the browser
3. Test with a sample query

## Troubleshooting

### App shows "Oh no. Error running app"

**Solution 1: Check logs**
- In Streamlit Cloud dashboard, click "Manage app"
- Click "View logs"
- Look for error messages

**Solution 2: Verify secrets are set**
- Go to app Settings → Secrets
- Ensure all API keys are configured
- Click "Save" to trigger redeploy

**Solution 3: Check requirements.txt**
- Ensure `phases/phase-0-foundation/requirements.txt` has all dependencies
- Streamlit Cloud installs from this file

### "ModuleNotFoundError: No module named 'src'"

**Solution:**
- Ensure `__init__.py` files exist in all phase directories
- Check that `app.py` is at the root level
- Verify path setup in `app.py` is correct

### API Key Errors

**Solution 1: Verify key format**
- Gemini keys start with `AIzaSy`
- Groq keys start with `gsk_`
- GitHub keys start with `crsr_` or `ghp_`

**Solution 2: Check key validity**
- Test keys locally first
- Ensure keys haven't been revoked
- Check API quota hasn't been exceeded

**Solution 3: Rotate keys**
- If one key is exhausted, the system falls back to others
- Add new keys to Streamlit Cloud secrets

### Slow Performance

**Solution 1: First load is slow**
- Streamlit initializes RAG engine on first load
- This can take 30-60 seconds
- Subsequent queries are faster (5-10 seconds)

**Solution 2: Optimize**
- Use Gemini Flash 2.0 (faster than Pro)
- System automatically uses fastest available model
- Fallback to Groq if Gemini is slow

## Local Testing Before Deployment

Test locally to ensure everything works:

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r phases/phase-0-foundation/requirements.txt

# 3. Create .env file
cp phases/phase-0-foundation/.env.example phases/phase-0-foundation/.env
# Edit .env with your API keys

# 4. Run app
streamlit run app.py

# 5. Test in browser
# Open http://localhost:8501
```

## File Structure for Deployment

Streamlit Cloud expects this structure:

```
repository/
├── app.py                          # Main entry point (REQUIRED)
├── streamlit.toml                  # Streamlit config
├── .streamlit/
│   ├── config.toml                 # Theme config
│   └── secrets.toml.example        # Secrets template (not committed)
├── phases/
│   ├── phase-0-foundation/
│   │   ├── __init__.py
│   │   ├── .env                    # Local only (not committed)
│   │   └── requirements.txt        # Dependencies
│   ├── phase-1-collection/
│   ├── phase-2-processing/
│   ├── phase-3-retrieval/
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── rag_engine.py
│   │       └── shared.py
│   ├── phase-4-orchestration/
│   │   └── src/
│   │       ├── __init__.py
│   │       └── scheduler.py
│   └── phase-5-frontend/
│       ├── __init__.py
│       └── app.py
└── README.md
```

## Environment Variables

The app loads environment variables in this order:

1. **Streamlit Cloud Secrets** (highest priority)
   - Set in Streamlit Cloud dashboard
   - Used in production

2. **.env file** (local development)
   - Located at `phases/phase-0-foundation/.env`
   - Not committed to GitHub
   - Used for local testing

3. **System environment variables** (fallback)
   - Set in shell/terminal
   - Used if above not available

## Monitoring

### Check App Status

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. View:
   - Last deployed time
   - Current status (running/error)
   - Resource usage

### View Logs

1. Click "Manage app"
2. Click "View logs"
3. See real-time logs and errors

### Restart App

1. Click "Manage app"
2. Click "Reboot app"
3. App will restart and redeploy

## Updating the App

To update the app after making changes:

1. Make changes locally
2. Test with `streamlit run app.py`
3. Commit and push to GitHub:
   ```bash
   git add -A
   git commit -m "Update: description of changes"
   git push origin main
   ```
4. Streamlit Cloud automatically redeploys within 1-2 minutes

## Performance Tips

1. **First load**: 30-60 seconds (normal)
2. **Subsequent queries**: 5-10 seconds
3. **Caching**: Streamlit caches embeddings and models
4. **API keys**: System cycles through 3 Gemini keys for better performance

## Support

For issues:

1. Check Streamlit Cloud logs
2. Review TROUBLESHOOTING.md
3. Check GitHub Issues
4. Review Streamlit documentation: https://docs.streamlit.io

## Security Notes

⚠️ **IMPORTANT**: Never commit API keys to GitHub

- Use `.gitignore` to exclude `.env` and `secrets.toml`
- Set secrets in Streamlit Cloud dashboard only
- Rotate keys regularly
- Monitor API usage for suspicious activity

## Cost Considerations

Streamlit Cloud free tier includes:
- 1 app
- 1 GB storage
- Shared CPU
- Community support

For production use, consider:
- Streamlit Cloud Pro ($5/month per app)
- Dedicated resources
- Priority support
- Custom domains

## Next Steps

1. Deploy to Streamlit Cloud
2. Share the app URL with users
3. Monitor performance and logs
4. Update as needed
5. Consider upgrading to Pro for production use
