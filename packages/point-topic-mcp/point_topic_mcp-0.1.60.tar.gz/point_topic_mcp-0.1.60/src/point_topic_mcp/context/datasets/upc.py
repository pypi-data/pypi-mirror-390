
def get_dataset_summary():
    """This will be visible to the agent at all times, so keep it short, but let the agent know if the dataset can answer the question of the user."""
    return """
    UK broadband infrastructure availability data at postcode level. 
    Monthly snapshots showing operator footprint and premises coverage (not subscriber numbers). 
    Also contains the whole UK at postcode granularity, with geographic and demographic data.
    """


def get_db_info():
    return f"""
    {DB_INFO}

    {DB_SCHEMA}

    {SQL_EXAMPLES}
    """

DB_INFO = """

Broadband availability datasets for the UK at postcode granularity. Monthly snapshots.

UPC stands for unit post code, so all UPC tables are at postcode granularity

The reported_at field always lands on the first day of the month.

Remember that footprint/premises passed is not the same as market share. 
The market share would be the number of subscribers (paying customers), 
wheras the footprint is the number of premises that have availability

Key UK Broadband Market Facts (for sanity checking):
- Total UK premises: approximately 33 million
- Total UK households: approximately 30 million  
- Total UK population: approximately 67 million
- If your query results show significantly different totals, double-check your calculations

Always sanity check your results against these known facts.

CRITICAL: Market Share and Total Premises Calculations

upc_core.reports.fact_operator is unique per postcode,operator,tech and reported_at
so when getting sums of premises by joining upc on postcode,reported_at you must
get the distinct list of postcodes, as there can be duplicates when an operator has multiple technology

MARKET SHARE CALCULATIONS:
- For calculating TOTAL UK premises or market denominators, ALWAYS use upc_core.reports.upc_output directly
- Careful when summing premises from upc_core.reports.fact_operator joins as this can creates duplicates for shared postcodes
- Individual operator footprints: Use distinct postcodes from upc_core.reports.fact_operator joined to upc_output
- Total market size: Use SUM(premises) FROM upc_core.reports.upc_output directly

Make a note that this is AVAILABILITY market share, not based on Subscribers

Example pattern for market share:
1. Operator footprint: select sum(premises) from upc_core.reports.fact_operator f join upc_core.reports.upc_output u USING(postcode) WHERE f.operator = 'X' GROUP BY postcode
2. Total market: select sum(premises) from upc_core.reports.upc_output (separate query, not derived from operator data)

Note the virgin media isps are as follows:
'Virgin Media RFOG'
'Virgin Cable'

'nexfibre Virgin Media' is considered an altnet in our systems

For altnet queries we exclude Openreach ops and virgin media ops 

for example:
where operator not in ('BT','Sky','TalkTalk','Vodafone','Virgin Cable','Virgin Media RFOG')
  and operator not like '%nexfibre%'

we also group together the CityFibre ops:
when operator like '%CityFibre%' then 'CityFibre'

To see the full list of operators available in the database, use the get_distinct_value_list('upc','operator') tool.

CRITICAL: WHEN TO USE TIME SERIES VS NON-TIME-SERIES TABLES
-----------------------------------------------------------
Use the get_dataset_status() tool to check the latest available dates for each dataset.

The current/latest snapshot in the database is typically updated monthly.

1. For queries about "current", "latest", or specific dates that match the latest snapshot:
   - USE: upc_output and fact_operator (non-time-series tables)
   - REASON: Simpler queries, no date filtering needed, same results
   - CHECK: Use get_dataset_status() to confirm the latest upc_reported_at date
   
2. For queries explicitly about historical trends, comparisons over time, or dates BEFORE the latest snapshot:
   - USE: upc_output_time_series and fact_operator_time_series
   - REASON: Contains historical snapshots

3. If the user asks about a specific quarter/date and that IS the latest snapshot (check with get_dataset_status), use the non-time-series tables.

CRITICAL: OPERATOR NAME CANONICALIZATION
----------------------------------------
CityFibre appears in the database as multiple variants: 'CityFibre Vodafone', 'CityFibre TalkTalk', etc.
These are wholesale relationships where CityFibre provides infrastructure to other ISPs.

WHEN COUNTING DISTINCT OPERATORS OR CALCULATING OVERBUILD:
- You MUST canonicalize operator names BEFORE counting distinct values
- ALWAYS use: case when operator like '%CityFibre%' then 'CityFibre' else operator end
- Then count distinct on the canonicalized name
- This applies to BOTH time-series and non-time-series queries

WRONG (counts CityFibre variants as separate operators):
  count(distinct operator) where operator not in (...)

RIGHT (canonicalizes first, then counts):
  select postcode, 
    case when operator like '%CityFibre%' then 'CityFibre' else operator end as operator_canonical
  from fact_operator
  where operator not in (...)
  -- THEN count distinct operator_canonical

Tips for UPC tables:
1. For fttp queries to fact_operator, you can use the tech like '%fttp%' filter because there is one type of value 'fttponly'
2. If the answer only requires current data then use the upc_output or fact_operator tables directly. No need to use the time series tables.
3. CRITICAL FOR MARKET SHARE AND AVAILABILITY SUMS: Total UK premises must come from upc_output directly. Never derive totals from fact_operator joins.
4. If the question is about how many homes were passed by an operator - Then use the households metric in the upc output table.
5. **PREFER fact_altnet/fact_altnet_time_series for altnet queries** - these tables have CityFibre canonicalization and Openreach/VM exclusions pre-applied. Much simpler than manual filtering on fact_operator.
   - Still filter out nexfibre if using strict altnet definition: `where operator != 'nexfibre Virgin Media'`
   - No need to manually canonicalize CityFibre or exclude BT/Sky/TalkTalk/Vodafone/Virgin - already done
"""

DB_SCHEMA = """
upc_core.reports.fact_operator_time_series (
	postcode varchar(16777216) comment 'name of postcode',
	operator varchar(16777216) comment 'name of operator',
	tech varchar(16777216) comment 'technology',
	fastest_up number(38,2) comment 'fastest upload speed',
	fastest_down number(38,0) comment 'fastest download speed',
	activated_date date comment 'date when this footprint happenws',
	reported_at date comment 'represent for version of postcode (vtable-tbb)'
)

upc_core.reports.fact_operator (
    # this is the same as upc_core.reports.fact_operator_time_series but with only the most recent snapshot of data
)

upc_core.reports.fact_altnet_time_series (
	postcode varchar(16777216) comment 'name of postcode',
	operator varchar(16777216) comment 'canonicalized altnet operator name (CityFibre variants collapsed)',
	tech varchar(16777216) comment 'technology',
	reported_at date comment 'represent for version of postcode (vtable-tbb)'
)

upc_core.reports.fact_altnet (
    # this is the same as upc_core.reports.fact_altnet_time_series but with only the most recent snapshot of data
    # CRITICAL: Use this table for altnet queries - it has CityFibre canonicalization and openreach/VM exclusions already applied
    # Excluded operators: BT, Sky, TalkTalk, Vodafone, Virgin Cable, Virgin Media RFOG, KCOM Lightstream
    # NOTE: Currently includes 'nexfibre Virgin Media' which may need filtering depending on your definition of altnet
)

upc_core.reports.upc_output_time_series (
	postcode varchar(16777216) comment 'key for upc_output, unique per reporting month',
	mapinfo_id number(18,0) comment 'map information identification code',
	post_sector varchar(16777216) comment 'higher level postcode grouping',
	northings number(38,0) comment 'distance in metres north of national grid origin',
	eastings number(38,0) comment 'distance in metres east of national grid origin',
	coa_code varchar(16777216) comment 'ons-defined code for the census output area in which the upc is located',
	lsoa varchar(16777216) comment 'ons-defined code for the lower super output area in which the upc is located',
	msoa_and_im varchar(16777216) comment 'ons-defined code for the middle super output area or intermediate zone in scotland in which the upc is located',
	la_code varchar(16777216) comment 'local authority area code',
	la_name varchar(16777216) comment 'local authority area name',
	government_region varchar(16777216) comment 'government region',
	country varchar(16777216) comment 'name of the nation in which the upc is located',
	population number(38,2) comment 'estimated population of the upc',
	premises number(38,2) comment 'total number of households and business premises (sites or workplaces) in the upc',
	households number(38,0) comment 'estimated number of households in the upc',
	bus_sites_total number(38,2) comment 'estimated number of business premises (sites or workplaces) in the upc',
	mdfcode varchar(16777216) comment 'identifier for bt/openreach exchange serving the upc',
	exchange_name varchar(16777216) comment 'name of exchange serving the upc',
	cityfibre_postcode_passed varchar(1) comment 'whether the upc is within cityfibre halo (200m-500m)',
)

upc_core.reports.upc_output (
    # this is the same as upc_core.reports.upc_output_time_series but with only the most recent snapshot of data
)

"""

SQL_EXAMPLES = [
    {
        'request': 'Show me the growth in FTTP coverage by local authority over the last 6 months.',
        'response': """
-- This query demonstrates a time-series comparison pattern.
-- It calculates the change in the number of postcodes with FTTP coverage between the most recent data and data from 6 months ago.
with fttp_coverage_by_month as (
  select
    T2.la_name,
    T1.reported_at,
    -- CRITICAL: Must use distinct postcodes when aggregating from fact_operator joins
    count(distinct T1.postcode) as fttp_postcode_count
  from upc_core.reports.fact_operator_time_series as T1
  join upc_core.reports.upc_output_time_series as T2 
    on T1.postcode = T2.postcode and T1.reported_at = T2.reported_at
  where 
    T1.tech like '%fttp%'
    -- Filter for only the two dates we care about for comparison
    and T1.reported_at in (
      (select max(reported_at) from upc_core.reports.fact_operator_time_series),
      (select dateadd(month, -6, max(reported_at)) from upc_core.reports.fact_operator_time_series)
    )
  group by 1, 2
)
select
  la_name,
  -- Use conditional aggregation (max + case) to pivot the two time periods into separate columns
  max(case when reported_at = (select max(reported_at) from fttp_coverage_by_month) then fttp_postcode_count else 0 end) as current_fttp_postcodes,
  max(case when reported_at = (select min(reported_at) from fttp_coverage_by_month) then fttp_postcode_count else 0 end) as past_fttp_postcodes,
  current_fttp_postcodes - past_fttp_postcodes as growth_in_postcodes
from fttp_coverage_by_month
group by la_name
having growth_in_postcodes > 0
order by growth_in_postcodes desc
limit 10"""
    },
    {
        'request': 'What is the current FTTP footprint of the top 10 operators?',
        'response': """
-- This query demonstrates the essential pattern for calculating an operator's footprint.
-- It correctly joins a unique list of operator postcodes with premise counts from the main output table.
select
  -- Grouping similar operators like 'CityFibre' is a common and useful practice
  case when f.operator like '%CityFibre%' then 'CityFibre' else f.operator end as operator_group,
  round(sum(u.premises)) as total_premises_passed
from
  -- CRITICAL: Start with a subquery on fact_operator to get a unique list of postcodes per operator for the desired tech
  (
    select distinct
      operator,
      postcode
    from upc_core.reports.fact_operator
    where tech like '%fttp%'
  ) as f
-- Join to the current upc_output snapshot to get the number of premises for each postcode
join upc_core.reports.upc_output as u on f.postcode = u.postcode
group by
  operator_group
order by
  total_premises_passed desc
limit 10"""
    },
    {
        'request': 'What is the FTTP availability market share for each altnet operator?',
        'response': """
-- This query demonstrates the correct, multi-step pattern for calculating market share.
-- It correctly calculates the numerator (operator footprint) and denominator (total market) separately.
with
  -- Step 1: Calculate each altnet's distinct FTTP footprint in premises.
  operator_footprint as (
    select
      f.operator,
      sum(u.premises) as operator_premises
    from (
      select distinct operator, postcode from upc_core.reports.fact_operator where tech like '%fttp%'
    ) as f
    join upc_core.reports.upc_output u on f.postcode = u.postcode
    where f.operator not in ('BT','Sky','TalkTalk','Vodafone','Virgin Cable','Virgin Media RFOG')
      and f.operator not like '%nexfibre%'
    group by f.operator
  ),
  -- Step 2: Calculate the TOTAL UK FTTP market size.
  -- CRITICAL: This is derived from upc_output, filtered to postcodes that have ANY FTTP provider.
  total_fttp_market as (
    select sum(premises) as total_market_premises
    from upc_core.reports.upc_output
    where postcode in (select distinct postcode from upc_core.reports.fact_operator where tech like '%fttp%')
  )
select
  op.operator,
  op.operator_premises,
  -- Use a cross join to apply the total market size denominator to every row
  tm.total_market_premises,
  round((op.operator_premises / tm.total_market_premises) * 100, 2) as market_share_percentage
from operator_footprint as op
cross join total_fttp_market as tm
order by market_share_percentage desc"""
    },
    {
        'request': 'Show me the top 10 local authorities with the most competition between CityFibre and other altnets.',
        'response': """
-- This query demonstrates how to find "overbuild" or geographic overlap between different groups of operators.
-- It uses intersect to find the common postcodes between two distinct sets.
with
  -- Create a set of postcodes where CityFibre is present
  cityfibre_postcodes as (
    select distinct postcode
    from upc_core.reports.fact_operator
    where operator like '%CityFibre%'
  ),
  -- Create a set of postcodes where other altnets are present
  other_altnet_postcodes as (
    select distinct postcode
    from upc_core.reports.fact_operator
    where operator not in ('BT','Sky','TalkTalk','Vodafone','Virgin Cable','Virgin Media RFOG')
      and operator not like '%CityFibre%'
      and operator not like '%nexfibre%'
  ),
  -- Find the intersection of the two sets to identify overbuild postcodes
  overbuild_postcodes as (
    select postcode from cityfibre_postcodes
    intersect
    select postcode from other_altnet_postcodes
  )
-- Aggregate the results by Local Authority to find the most competitive areas
select
  u.la_name,
  round(sum(u.premises)) as overbuilt_premises,
  count(o.postcode) as overbuilt_postcode_count
from overbuild_postcodes as o
join upc_core.reports.upc_output as u on o.postcode = u.postcode
group by u.la_name
order by overbuilt_premises desc
limit 10"""
    },
    {
        'request': 'Show me altnet FTTP network overbuild: how many premises were passed by 1, 2, 3, 4, 5+ altnet FTTP networks',
        'response': """
-- PREFERRED METHOD: Use fact_altnet table (already has CityFibre canonicalized and exclusions applied)
with
  -- Count distinct operators per postcode
  operator_count_per_postcode as (
    select
      postcode,
      count(distinct operator) as altnet_count
    from upc_core.reports.fact_altnet
    where tech like '%fttp%'
      and operator != 'nexfibre Virgin Media'  -- exclude if using strict altnet definition
    group by postcode
  )
-- Aggregate premises by overbuild level
select
  altnet_count as number_of_altnet_fttp_networks,
  round(sum(u.premises), 0) as premises_passed
from operator_count_per_postcode o
join upc_core.reports.upc_output u using (postcode)
group by altnet_count
order by altnet_count asc"""
    },
    {
        'request': 'Show me altnet FTTP network overbuild using fact_operator (manual canonicalization)',
        'response': """
-- ALTERNATIVE METHOD: Manual canonicalization using fact_operator (use when you need more control)
-- CRITICAL: This demonstrates the CORRECT pattern for counting operators per postcode
-- Must canonicalize CityFibre variants BEFORE counting distinct operators
with
  -- Step 1: Get all altnet FTTP presence and canonicalize operator names
  altnet_fttp as (
    select
      postcode,
      case
        when operator like '%CityFibre%' then 'CityFibre'
        else operator
      end as operator_canonical
    from upc_core.reports.fact_operator
    where tech like '%fttp%'
      and operator not in ('BT','Sky','TalkTalk','Vodafone','Virgin Cable','Virgin Media RFOG')
      and operator not like '%nexfibre%'
    group by postcode, operator_canonical
  ),
  -- Step 2: Count distinct CANONICAL operators per postcode
  operator_count_per_postcode as (
    select
      postcode,
      count(distinct operator_canonical) as altnet_count
    from altnet_fttp
    group by postcode
  )
-- Step 3: Aggregate premises by overbuild level
select
  altnet_count as number_of_altnet_fttp_networks,
  round(sum(u.premises), 0) as premises_passed
from operator_count_per_postcode o
join upc_core.reports.upc_output u using (postcode)
group by altnet_count
order by altnet_count asc"""
    }
]
