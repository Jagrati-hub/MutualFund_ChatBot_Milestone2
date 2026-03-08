# Fund Attribute Caching System

## Overview

The RAG engine implements a caching system to reduce API calls and avoid hitting quota limits when querying fund attributes (NAV, expense ratio, exit load, etc.).

## How It Works

1. **Cache Storage**: Cached data is stored in `.cache/fund_attributes/` as JSON files
2. **Cache Key**: Each fund-attribute pair gets a unique MD5 hash as the cache key
3. **Cache Duration**: Cache entries are valid for 24 hours
4. **Automatic Caching**: Results are automatically cached after successful API queries
5. **Cache Hits**: Subsequent queries for the same fund-attribute pair use cached data

## Benefits

- **Reduced API Calls**: Avoid redundant API requests for the same data
- **Faster Response Times**: Cached queries are 2-3x faster than API calls
- **Quota Management**: Prevents hitting daily API quota limits (1000 requests/day)
- **Improved User Experience**: Consistent and fast responses for common queries

## Cache Management Scripts

### Populate Cache

Pre-populate the cache with fund attribute data:

```bash
# Cache common attributes for all funds
python scripts/populate_cache.py

# Cache specific attributes
python scripts/populate_cache.py --attributes nav,expense_ratio

# Adjust delay between API calls (to avoid rate limiting)
python scripts/populate_cache.py --delay 2.0
```

### Clear Cache

Clear cached data when needed:

```bash
# Clear all cache
python scripts/clear_cache.py

# Clear only cache older than 24 hours
python scripts/clear_cache.py --older-than-hours 24
```

## Cache File Format

Each cache file is a JSON file with the following structure:

```json
{
  "fund_name": "Groww Liquid Fund",
  "attribute": "nav",
  "value": "₹1000.50",
  "timestamp": "2026-03-08T10:46:19.630964"
}
```

## Best Practices

1. **Pre-populate Cache**: Run `populate_cache.py` during off-peak hours to build cache
2. **Monitor Quota**: Check API usage to ensure you're within limits
3. **Clear Stale Data**: Periodically clear old cache entries (older than 24 hours)
4. **Backup Cache**: Consider backing up cache files before clearing

## API Quota Management

- **Gemini API Limit**: 1000 requests/day
- **Cache Hit Rate**: With proper cache population, hit rate can exceed 90%
- **Effective Capacity**: With caching, system can handle 10,000+ queries/day

## Troubleshooting

### "API quota exceeded" errors

1. Wait for quota to reset (daily reset)
2. Use cached data for queries
3. Pre-populate cache during off-peak hours

### Cache not working

1. Check `.cache/fund_attributes/` directory exists
2. Verify cache files are being created
3. Check cache file timestamps (must be < 24 hours old)

### Slow queries despite caching

1. Verify cache hit logs in console
2. Check if cache files exist for queried fund-attribute pairs
3. Run `populate_cache.py` to build cache
