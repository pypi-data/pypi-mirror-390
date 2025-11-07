# Query Consistency Fix - v0.1.59

## The Problem
Chat agent returned wildly different altnet overbuild results vs direct SQL.

## Root Causes
1. **CityFibre operator name variants** - 6 variants counted as separate operators
2. **No nexfibre exclusion** - nexfibre Virgin Media incorrectly counted as altnet
3. **No dataset status tool** - agent couldn't check latest snapshot dates
4. **fact_altnet tables undocumented** - pre-computed altnet tables existed but agent didn't use them

## The Fix

### 1. Operator Canonicalization
Added explicit rules to collapse CityFibre variants before counting

### 2. nexfibre Exclusion
Added to all altnet query patterns: `and operator != 'nexfibre Virgin Media'`

### 3. Dataset Status Tool
Added `get_dataset_status()` tool that checks `upc_client._status.upc_status` for latest dates

### 4. fact_altnet Tables (New)
Added to schema with guidance to prefer over manual filtering:
- `fact_altnet` / `fact_altnet_time_series` 
- CityFibre already canonicalized
- Openreach/VM already excluded
- Simplifies queries from 30+ lines to ~14 lines

## Results

| Version | 1 Altnet | 2 Altnets | 3 Altnets | 4+ Altnets |
|---------|----------|-----------|-----------|------------|
| Chat (wrong) | 9.6M | 1.6M | 3.1M | 881k+ |
| Direct SQL (better) | 13.3M | 1.9M | 180k | 17k |
| **Fixed (correct)** | **13.0M** | **1.1M** | **64k** | **2k** |

## Install
```bash
pip install --upgrade point-topic-mcp==0.1.59
```

## What Changed
- Added `get_dataset_status()` tool
- Added `fact_altnet` / `fact_altnet_time_series` to schema
- Added nexfibre exclusion guidance
- Added simplified altnet query example using fact_altnet
