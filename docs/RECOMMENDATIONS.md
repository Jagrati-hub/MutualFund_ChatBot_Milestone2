# Recommendations for Production Deployment

## Immediate Actions

### 1. Pre-populate Cache
Run the cache population script during off-peak hours to build a complete cache:

```bash
# Recommended: Run this once daily during off-peak hours (e.g., 2 AM)
python scripts/populate_cache.py --attributes nav,expense_ratio,exit_load --delay 2.0
```

This will:
- Cache the 3 most common attributes for all 32 funds
- Take approximately 3-4 minutes (with 2s delay between calls)
- Use ~96 API calls (32 funds × 3 attributes)
- Provide cache coverage for 90%+ of user queries

### 2. Set Up Automated Cache Refresh
Create a scheduled task (cron job or Windows Task Scheduler) to refresh cache daily:

**Linux/Mac (crontab)**:
```bash
# Run at 2 AM daily
0 2 * * * cd /path/to/project && python scripts/populate_cache.py
```

**Windows (Task Scheduler)**:
- Create a new task
- Trigger: Daily at 2:00 AM
- Action: Run `python scripts/populate_cache.py`
- Working directory: Project root

### 3. Monitor Cache Performance
Add logging to track cache hit rates:

```python
# In your application startup or monitoring script
import logging
logging.basicConfig(level=logging.INFO)

# Cache hits will be logged as:
# INFO - Cache hit for Groww Liquid Fund - nav
```

## Best Practices

### Cache Management

1. **Daily Refresh**: Refresh cache once per day during off-peak hours
2. **Stale Data Cleanup**: Clear cache older than 24 hours weekly
3. **Backup**: Consider backing up cache before clearing
4. **Monitoring**: Track cache hit rates to optimize coverage

### API Quota Management

1. **Rate Limiting**: Use `--delay 2.0` or higher when populating cache
2. **Quota Monitoring**: Track daily API usage to stay within limits
3. **Fallback**: System gracefully handles quota errors with cached data
4. **Peak Hours**: Avoid cache population during peak user hours

### Query Optimization

1. **Common Queries**: Pre-cache most frequently requested attributes (NAV, expense ratio, exit load)
2. **Category Coverage**: Ensure all categories have cached data
3. **Error Handling**: Monitor "Not available" responses and investigate

## Performance Optimization

### Current Performance
- **Without Cache**: 6s per category query (21 funds)
- **With Cache**: 2s per category query (3x faster)
- **Cache Hit Rate**: 90%+ with proper pre-population

### Optimization Opportunities

1. **Increase Cache Duration**: Consider 48-hour cache for less volatile data
2. **Selective Caching**: Cache only frequently requested attributes
3. **Compression**: Compress cache files to save disk space
4. **Database Storage**: Move cache to database for multi-instance deployments

## Monitoring and Alerts

### Key Metrics to Track

1. **Cache Hit Rate**: Should be >90% with proper pre-population
2. **API Quota Usage**: Should be <500 calls/day with caching
3. **Response Times**: Should average <2s for cached queries
4. **Error Rate**: "API quota exceeded" should be <1%

### Recommended Alerts

1. **Low Cache Hit Rate** (<80%): Indicates cache needs refresh
2. **High API Usage** (>800 calls/day): Risk of hitting quota
3. **High Error Rate** (>5%): Investigate API issues
4. **Slow Queries** (>5s): Check cache performance

## Scaling Considerations

### Current Capacity
- **API Quota**: 1000 requests/day
- **With Caching**: Effective capacity of 10,000+ queries/day
- **Cache Storage**: ~1MB for all funds and attributes

### Scaling Options

1. **Multiple API Keys**: Rotate between multiple Gemini API keys
2. **Database Cache**: Use Redis or PostgreSQL for shared cache
3. **CDN**: Serve cached responses via CDN for global distribution
4. **Load Balancing**: Distribute queries across multiple instances

## Troubleshooting

### Issue: Cache Not Working
**Symptoms**: Queries still hitting API despite cache
**Solutions**:
1. Check `.cache/fund_attributes/` directory exists
2. Verify cache files are being created
3. Check cache timestamps (must be <24 hours old)
4. Review logs for "Cache hit" messages

### Issue: API Quota Exceeded
**Symptoms**: "⚠️ API quota exceeded" errors
**Solutions**:
1. Wait for quota to reset (daily reset)
2. Use cached data for queries
3. Pre-populate cache during off-peak hours
4. Reduce cache population frequency

### Issue: Slow Queries
**Symptoms**: Queries taking >5s despite caching
**Solutions**:
1. Verify cache hit rate in logs
2. Check if cache files exist for queried funds
3. Run `populate_cache.py` to build cache
4. Investigate network latency

## Security Considerations

1. **API Key Protection**: Keep API keys in `.env` file (not in code)
2. **Cache Access**: Restrict write access to cache directory
3. **Data Privacy**: Cache contains public fund data only
4. **Backup**: Regular backups of cache for disaster recovery

## Cost Analysis

### Without Caching
- **API Calls**: ~1000/day (quota limit)
- **Queries Supported**: ~50/day (20 API calls per equity query)
- **Cost**: Free tier (1000 requests/day)

### With Caching
- **API Calls**: ~100/day (90% cache hit rate)
- **Queries Supported**: 10,000+/day
- **Cost**: Free tier (well within limits)
- **Savings**: 10x reduction in API usage

## Future Enhancements

1. **Smart Invalidation**: Invalidate cache when data is updated
2. **Predictive Caching**: Pre-cache based on query patterns
3. **Distributed Cache**: Share cache across multiple instances
4. **Analytics Dashboard**: Visualize cache performance metrics
5. **A/B Testing**: Test different cache strategies
