# Phase 5: Frontend (Streamlit App - Multi-Page)

## Purpose
User-facing chat interface and admin dashboard for managing the FAQ assistant.

## Files in This Phase

### Main Application
- `app.py` - Main chat interface
- `pages/admin.py` - Admin dashboard page

### Configuration
- `.streamlit/config.toml` - Streamlit theme (Groww colors)

## Main Page Features
- Hero section with Groww theme (mint green #00d09c)
- 3 example question buttons
- Chat history with improved styling
- Enhanced chat input textbox with mint green border
- ⚙️ button for admin access

## Admin Dashboard Features
- Dark sidebar with admin controls
- System status monitoring
- Pipeline controls (Run Now, Clear Cache)
- Cache statistics
- Fund statistics
- Activity logs
- "← Back to Chat" button

## Latest Enhancements
✅ Improved UI - Mint green textbox with better alignment
✅ Multi-page - Separate admin dashboard
✅ Groww Theme - Premium mint green colors
✅ Admin Controls - Full pipeline management

## Query Handling
1. User enters query
2. `handle_query()` validates and processes
3. `rag_engine.answer()` retrieves and generates
4. Web links automatically removed
5. Answer + source link displayed

## Status
✅ Complete - All features implemented and deployed
