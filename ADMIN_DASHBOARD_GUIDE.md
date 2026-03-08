# Admin Dashboard Guide

## 🎯 Quick Access

### Method 1: Sidebar Button
1. Open http://localhost:8502
2. Look at the left sidebar
3. Click **📊 Admin Dashboard** button
4. You'll be taken to the admin page

### Method 2: Direct URL
```
http://localhost:8502?page=admin
```

---

## 📊 Admin Dashboard Features

### System Status
- **Scheduler Status**: Shows if the background scheduler is active
- **Next Update**: When the next automatic data refresh will occur
- **Total Funds**: Total number of mutual fund schemes (32)

### Pipeline Controls

#### Run Data Pipeline Now
- Manually trigger data scraping and ingestion
- Updates all fund data from Groww
- Shows progress in real-time
- Displays success/error messages

#### Clear Cache
- Removes all cached fund attributes
- Forces fresh data retrieval on next query
- Useful if data seems stale
- Instant operation

### Cache Statistics
- **Cached Entries**: Number of fund-attribute pairs cached
- **Cache Size**: Total disk space used by cache
- **Cache TTL**: How long cache is valid (24 hours)

### Fund Statistics
- **Equity Funds**: 21 schemes
- **Debt Funds**: 6 schemes
- **Hybrid Funds**: 3 schemes
- **Commodity Funds**: 2 schemes

### Recent Activity
- System status and logs
- Pipeline execution history
- Error messages (if any)

---

## 🔄 Common Tasks

### Task 1: Refresh All Data
1. Click **▶️ Run Data Pipeline Now**
2. Wait for completion (usually 30-60 seconds)
3. See success message
4. Data is now fresh

### Task 2: Clear Stale Cache
1. Click **🗑️ Clear Cache**
2. See success message
3. Next query will fetch fresh data
4. Cache will rebuild automatically

### Task 3: Check System Health
1. Look at **System Status** section
2. Verify scheduler is **🟢 Active**
3. Check **Next Update** time
4. Verify **Total Funds** is 32

### Task 4: Monitor Cache Usage
1. Look at **Cache Statistics**
2. Check number of cached entries
3. Monitor cache size
4. Clear if needed

---

## 🎨 UI Theme

The admin dashboard uses the same premium Groww theme as the main chat:
- **Mint Green**: Primary color (#00d09c)
- **Gradients**: Smooth color transitions
- **Shadows**: Depth and elevation
- **Professional**: Clean, modern design

---

## 🔐 Security Note

The admin dashboard is currently accessible to anyone with the URL. In production, consider adding:
- Password protection
- API key authentication
- IP whitelisting
- Session management

---

## 📱 Responsive Design

The admin dashboard works on:
- ✅ Desktop (1920x1080)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

---

## 🚀 Navigation

### From Admin to Chat
- Click **← Back** button at top-left
- Or open http://localhost:8502

### From Chat to Admin
- Click **📊 Admin Dashboard** in sidebar
- Or open http://localhost:8502?page=admin

---

## 📊 Metrics Explained

### Scheduler Status
- **🟢 Active**: Background scheduler is running
- **🔴 Inactive**: Scheduler is stopped

### Next Update
- Shows the exact time of next automatic data refresh
- Updates happen every 24 hours by default

### Cache Statistics
- **Cached Entries**: Each fund-attribute pair (e.g., "Groww Liquid Fund:nav")
- **Cache Size**: Total KB used on disk
- **Cache TTL**: 24 hours (auto-expires)

### Fund Statistics
- Breakdown of all 32 funds by category
- Helps verify data completeness

---

## ⚠️ Troubleshooting

### Pipeline Fails
1. Check internet connection
2. Verify Groww website is accessible
3. Check API keys in .env
4. Try again in a few minutes

### Cache Not Clearing
1. Verify you clicked the button
2. Check file permissions
3. Try manual deletion: `python scripts/clear_cache.py`

### Scheduler Not Active
1. Check if app is running
2. Restart the app
3. Check logs for errors

---

## 📝 Example Workflow

1. **Morning**: Check admin dashboard
2. **See**: Next update scheduled for 2 PM
3. **Verify**: Cache has 50+ entries
4. **Monitor**: System status is active
5. **If needed**: Click "Run Pipeline" to refresh early
6. **Return**: Click "← Back" to chat interface

---

## 🎯 Summary

The admin dashboard provides:
- ✅ Real-time system monitoring
- ✅ Manual pipeline control
- ✅ Cache management
- ✅ Fund statistics
- ✅ Activity logs
- ✅ Easy navigation

**Access**: http://localhost:8502?page=admin or click sidebar button

**Status**: 🟢 READY TO USE
