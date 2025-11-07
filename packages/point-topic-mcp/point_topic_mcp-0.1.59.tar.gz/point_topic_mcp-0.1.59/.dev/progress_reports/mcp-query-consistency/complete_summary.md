# Query Consistency Investigation & Fix - Complete Summary

## What We Found

Investigated Jolanta's report of inconsistent altnet overbuild results between chat and non-chat query agents.

### The Main Issues

1. **CityFibre Name Variants (Critical)**
   - Database has 6 CityFibre variants (wholesale relationships with different ISPs)
   - Chat agent counted them as 6 separate operators
   - Inflated overbuild numbers dramatically

2. **Time-Series Table Misuse**
   - Agent using complex time-series tables for "Q3 2025" queries
   - Q3 2025 IS the latest snapshot, should use simpler static tables
   - Unnecessary complexity increased error surface

3. **nexfibre Virgin Media Exclusion (Bonus Bug)**
   - Discovered during investigation
   - nexfibre (80k postcodes) is Virgin Media O2 joint venture
   - Should be excluded from altnet queries
   - **Both chat AND non-chat versions had this bug**

### The Results

| Version | 1 Altnet | 2 Altnets | 3 Altnets | 4 Altnets | 5+ Altnets |
|---------|----------|-----------|-----------|-----------|------------|
| Chat (wrong) | 9.6M | 1.6M | 3.1M | 881k | 97k+ |
| Non-chat (better) | 13.3M | 1.9M | 180k | 17k | - |
| **Fixed (correct)** | **13.0M** | **1.2M** | **100k** | **8k** | - |

The fixed version is **more accurate than both previous versions**.

## The Fix

**Published: v0.1.57**

Updated `src/point_topic_mcp/context/datasets/upc.py`:

1. ✅ Added "CRITICAL: OPERATOR NAME CANONICALIZATION" section
   - Explains CityFibre variants
   - Shows WRONG vs RIGHT pattern
   - Emphasizes: canonicalize BEFORE counting

2. ✅ Added "CRITICAL: WHEN TO USE TIME SERIES VS NON-TIME-SERIES TABLES" section
   - Latest snapshot = 2025-09-01 (Q3 2025)
   - Use static tables for current/latest queries
   - Use time-series only for historical comparisons

3. ✅ Added explicit overbuild query SQL example
   - Shows correct 3-step canonicalization pattern

4. ✅ Added nexfibre exclusion to all altnet queries
   - Updated Virgin Media operator list
   - Added filter: `and operator not like '%nexfibre%'`

## Files Changed

- `src/point_topic_mcp/context/datasets/upc.py` - Updated dataset context with critical guidance
- `.dev/progress_reports/mcp-query-consistency/` - Investigation documentation
  - `2025-11-07_154500_bug_operator-canonicalization.md` - Technical breakdown
  - `summary_for_jolanta.md` - User-facing summary
  - `email_to_jolanta.txt` - Email draft

## Next Steps

1. Jolanta tests with: `pip install --upgrade point-topic-mcp==0.1.57`
2. Verify consistency across both agents
3. Monitor for any other operator name variant issues
4. Consider creating a canonical operator dimension table

## Key Takeaway

The MCP context is like an instruction manual for AI agents. Without explicit:
- Examples showing edge cases
- Warnings about data quirks
- Clear decision rules

...even smart agents make reasonable but incorrect assumptions. We went from "close enough" to "actually correct" by making the hidden knowledge explicit.

