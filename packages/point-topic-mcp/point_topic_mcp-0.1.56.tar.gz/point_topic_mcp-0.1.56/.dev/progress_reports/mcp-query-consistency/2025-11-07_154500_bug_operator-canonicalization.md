# bug: inconsistent altnet overbuild results between chat and non-chat agents

## problem identified
jolanta reported wildly different results for same query:
- non-chat (direct sql): 1 altnet = 13.3M premises, 2 altnets = 1.9M, 3 altnets = 180k, 4 altnets = 17k
- chat (mcp tools): 1 altnet = 9.6M premises, 2 altnets = 1.6M, 3 altnets = 3.1M, 4 altnets = 881k, **5-7 altnets appeared**

## root causes
1. **operator canonicalization not enforced before counting**
   - cityfibre has 6 variants: 'CityFibre Vodafone', 'CityFibre TalkTalk', etc
   - chat agent was doing `count(distinct operator)` directly
   - should canonicalize first: `case when operator like '%CityFibre%' then 'CityFibre' else operator end`

2. **unclear guidance on time-series vs non-time-series tables**
   - latest snapshot = 2025-09-01 (Q3 2025)
   - when user asks "Q3 2025", agent was using time-series tables with complex date filtering
   - should use simpler non-time-series tables (`upc_output`, `fact_operator`) for current data

3. **no explicit sql pattern for overbuild queries**
   - examples didn't show correct canonicalization-then-count pattern

## verification
ran both approaches:
```sql
-- WRONG (chat version): count(distinct operator) directly
-- result: 1=9.6M, 2=1.6M, 3=3.1M, 4=881k, 5=97k, 6=16k, 7=97

-- RIGHT (non-chat version): canonicalize then count
-- result: 1=13.3M, 2=1.9M, 3=180k, 4=17k
```

## fix implemented
**file: `src/point_topic_mcp/context/datasets/upc.py`**

### changes:
1. added "CRITICAL: WHEN TO USE TIME SERIES VS NON-TIME-SERIES TABLES" section
   - explicit rule: if query = latest snapshot (Q3 2025), use non-time-series tables
   - clear guidance: only use time-series for historical comparisons

2. added "CRITICAL: OPERATOR NAME CANONICALIZATION" section
   - explains cityfibre variants
   - shows WRONG vs RIGHT pattern
   - emphasizes: canonicalize BEFORE counting distinct

3. added new sql example for overbuild queries
   - demonstrates correct 3-step pattern:
     1. canonicalize operators
     2. count distinct canonical names
     3. aggregate by count

## next steps
- deploy to pypi
- test with jolanta's exact prompts
- monitor for consistency

## technical notes
- cityfibre appears as 6 variants due to wholesale relationships
- counting variants as separate operators inflates overbuild levels
- simpler queries (non-time-series) reduce error surface

