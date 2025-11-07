# Impact Analysis: Each Fix Applied Separately

## Query Results Comparison

### Test 1: NO Canonicalization, NO nexfibre Exclusion (WRONG - Original Chat Version)
```
 ALTNET_COUNT  PREMISES
            1  9,643,810
            2  1,646,543
            3  3,058,481
            4    881,252
            5     96,541
            6     16,237
            7         97
```
**Problem**: CityFibre variants counted as separate operators, inflated overbuild massively

### Test 2: WITH Canonicalization, NO nexfibre Exclusion (BETTER - Original Non-Chat Version)
```
 ALTNET_COUNT   PREMISES
            1  13,285,599
            2   1,860,217
            3     180,390
            4      16,755
```
**Better**: CityFibre correctly counted as one operator, but still includes nexfibre as altnet

### Test 3: WITH Canonicalization, WITH nexfibre Exclusion (CORRECT - Fixed Version)
```
 ALTNET_COUNT   PREMISES
            1  13,043,209
            2   1,156,972
            3     100,077
            4       7,912
```
**Correct**: Both issues fixed, most accurate representation

## Impact Analysis

### Canonicalization Fix (Test 1 → Test 2)
- **1 altnet**: 9.6M → 13.3M (+37.7%)
- **2 altnets**: 1.6M → 1.9M (+13.0%)
- **3 altnets**: 3.1M → 180k (-94.1%)
- **4-7 altnets**: Disappeared (were artifacts of counting CityFibre variants)

**Explanation**: Moving CityFibre-passed premises from the "5-7 altnets" artificial buckets back to the correct "1-4 altnets" buckets where they belong.

### nexfibre Exclusion Fix (Test 2 → Test 3)
- **1 altnet**: 13.3M → 13.0M (-1.8%, -242k)
- **2 altnets**: 1.9M → 1.2M (-37.8%, -703k)
- **3 altnets**: 180k → 100k (-44.5%, -80k)
- **4 altnets**: 17k → 8k (-52.7%, -9k)

**Explanation**: nexfibre operates in areas with high altnet presence. Removing it primarily reduces the "2-3 altnets" buckets as many nexfibre areas had one other altnet (creating "2" overbuild when there was actually only "1" altnet).

## Compound Effect

From Test 1 (wrong) to Test 3 (correct):
- **Changed dramatically**: Completely different distribution
- **Direction**: Shifted premises from high overbuild buckets (3-7) to lower overbuild buckets (1-2)
- **Reality**: Most altnet coverage is monopolistic or duopolistic, not the chaotic 5-7 way competition suggested by uncorrected data

## Business Impact

The uncorrected data suggested much higher competition levels than actually exist:
- Overstated high-competition areas (3+ altnets)
- Understated monopoly areas (1 altnet)
- Created phantom competition (5-7 altnets that don't exist)

This would lead to:
- ❌ Incorrect investment decisions
- ❌ Misleading competitive analysis
- ❌ Wrong market entry strategies

The corrected data provides a more realistic picture of the UK altnet market structure.

