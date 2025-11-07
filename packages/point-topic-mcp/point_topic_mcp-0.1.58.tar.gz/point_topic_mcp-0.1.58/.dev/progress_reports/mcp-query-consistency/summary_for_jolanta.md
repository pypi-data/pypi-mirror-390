# Query Consistency Fix - v0.1.58

## The Problem
Chat agent returned wildly different altnet overbuild results vs direct SQL.

## Root Causes
1. **CityFibre operator name variants** - 6 variants counted as separate operators instead of one
2. **No nexfibre exclusion** - nexfibre Virgin Media (80k postcodes) incorrectly counted as altnet
3. **No dataset status tool** - agent couldn't check latest snapshot dates dynamically

## The Fix

### 1. Operator Canonicalization (Critical)
Added explicit rules to collapse CityFibre variants before counting:
```sql
case when operator like '%CityFibre%' then 'CityFibre' else operator end
```

### 2. nexfibre Exclusion
Added to all altnet query patterns:
```sql
and operator not like '%nexfibre%'
```

### 3. Dataset Status Tool (New)
Added `get_dataset_status()` tool that queries `upc_client._status.upc_status` to:
- Check latest UPC snapshot date dynamically
- Determine if time-series tables needed
- Verify data freshness

## Results

| Version | 1 Altnet | 2 Altnets | 3 Altnets | 4+ Altnets |
|---------|----------|-----------|-----------|------------|
| Chat (wrong) | 9.6M | 1.6M | 3.1M | 881k+ |
| Direct SQL (better) | 13.3M | 1.9M | 180k | 17k |
| **Fixed (correct)** | **13.0M** | **1.2M** | **100k** | **8k** |

Fixed version is more accurate than both previous versions.

## Install
```bash
pip install --upgrade point-topic-mcp==0.1.58
```

## What Changed
- `src/point_topic_mcp/tools/database_tools.py` - Added `get_dataset_status()` tool
- `src/point_topic_mcp/context/datasets/upc.py` - Added canonicalization rules, nexfibre exclusion, status tool reference
