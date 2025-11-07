# MCP Query Consistency Fix - Summary

## The Problem

Your altnet overbuild query was returning wildly different results between:
- **Non-chat version**: 1 altnet = 13.3M, 2 altnets = 1.9M, 3 altnets = 180k, 4 altnets = 17k
- **Chat version**: 1 altnet = 9.6M, 2 altnets = 1.6M, 3 altnets = 3.1M, **4-7 altnets with inflated numbers**

## Root Causes

### 1. CityFibre Operator Name Variants (MAIN ISSUE)
CityFibre appears in the database as **6 different variants**:
- 'CityFibre Vodafone'
- 'CityFibre TalkTalk'  
- 'CityFibre Lit Fibre'
- 'CityFibre Giganet'
- 'CityFibre Zen Internet'
- 'CityFibre You Fibre'

These represent wholesale relationships where CityFibre provides infrastructure to other ISPs.

**The chat agent was counting these as 6 separate operators**, massively inflating overbuild counts.

### 2. Table Selection Confusion
When you asked about "Q3 2025", the chat agent was:
- Using complex time-series tables (`fact_operator_time_series`) with date filtering
- When it should have used simpler non-time-series tables (`fact_operator`) since Q3 2025 IS the latest snapshot

### 3. No Explicit Pattern for Overbuild Queries
The agent didn't have a clear example showing the correct 3-step pattern:
1. Canonicalize operator names (CityFibre* → 'CityFibre')
2. Count distinct canonical operators
3. Aggregate by count

## The Fix

**Version 0.1.56** adds three critical improvements to the UPC dataset context:

### 1. **CRITICAL: OPERATOR NAME CANONICALIZATION** section
Shows agents the WRONG vs RIGHT pattern:

**WRONG:**
```sql
count(distinct operator) where operator not in (...)
```

**RIGHT:**
```sql
select postcode, 
  case when operator like '%CityFibre%' then 'CityFibre' else operator end as operator_canonical
from fact_operator
where operator not in (...)
-- THEN count distinct operator_canonical
```

### 2. **CRITICAL: WHEN TO USE TIME SERIES VS NON-TIME-SERIES TABLES** section
Explicit guidance:
- Latest snapshot = 2025-09-01 (Q3 2025)
- For "current" or "Q3 2025" queries → use `upc_output` and `fact_operator`
- For historical comparisons → use `_time_series` tables

### 3. **New SQL example for altnet overbuild**
Shows the complete correct pattern with canonicalization before counting.

## Verification

Ran both query patterns against the same data:

**Without canonicalization (WRONG):**
```
1 altnet:  9,643,810 premises
2 altnets: 1,646,543 premises  
3 altnets: 3,058,481 premises
4 altnets:   881,252 premises
5 altnets:    96,541 premises
6 altnets:    16,237 premises
7 altnets:        97 premises
```

**With canonicalization (CORRECT):**
```
1 altnet:  13,285,599 premises
2 altnets:  1,860,217 premises
3 altnets:    180,390 premises
4 altnets:     16,755 premises
```

✅ Matches your non-chat version exactly!

## Next Steps

1. **Update your MCP installation:**
   ```bash
   pip install --upgrade point-topic-mcp==0.1.56
   ```

2. **Test with your original prompts:**
   - "Show me altnet FTTP network overbuild in Q3 2025: how many premises were passed by 1, 2, 3, 4 and 5 altnet FTTP networks"
   - "What was the overall FTTP coverage in Q3 2025?"

3. **Verify consistency:**
   - Chat results should now match direct SQL results
   - Agent should prefer simpler non-time-series tables for Q3 2025 queries
   - CityFibre should always be counted as one operator (not 6)

4. **Let me know:**
   - If you still see inconsistencies
   - If the agent is still using time-series tables when it shouldn't
   - If any other operators have similar variant issues

## Why This Happened

The MCP context is effectively the "instruction manual" for the AI agent. Without explicit:
- Examples showing canonicalization patterns
- Warnings about operator name variants
- Clear rules about table selection

...the agent was making reasonable but incorrect assumptions that led to inflated overbuild counts.

Think of it like giving someone directions: "turn left at the lights" works great if there's only one set of lights, but if there are six, you need to specify "turn left at the FIRST set of lights."

