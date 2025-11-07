from point_topic_utils import query_to_df
import sys
import json
import pandas as pd
from datetime import datetime
import os

def query_and_print_results(query: str, format='table'):
    """Execute query and print results in specified format"""
    try:
        print(f"Executing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        df = query_to_df(query)
        
        if df is None or df.empty:
            print("Query returned no results.")
            return None
            
        print(f"Query returned {len(df)} rows.")
        
        if format == 'json':
            print(df.to_json(indent=2))
        elif format == 'csv':
            print(df.to_csv(index=False))
        elif format == 'describe':
            print(f"\nDataFrame Info:")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print(f"\nFirst 10 rows:")
            print(df.head(10))
            if len(df) > 10:
                print(f"\n... and {len(df) - 10} more rows")
        else:  # default table format
            print(df.to_string(index=False))
            
        return df
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None

def save_query_results(query: str, filename: str = None):
    """Execute query and save results to CSV file"""
    try:
        df = query_to_df(query)
        if df is None or df.empty:
            print("No results to save.")
            return False
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../ai/query_results_{timestamp}.csv"
        
        # Ensure ai directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename} ({len(df)} rows)")
        return True
        
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False

def quick_check(table_name: str):
    """Quick data quality check on a table"""
    queries = [
        f"select COUNT(*) as row_count FROM {table_name}",
        f"select COUNT(DISTINCT *) as distinct_rows FROM {table_name}",
        f"select * FROM {table_name} LIMIT 5"
    ]
    
    print(f"\n=== Quick Check: {table_name} ===")
    for query in queries:
        print(f"\n{query}")
        query_and_print_results(query, format='describe')

def show_table_info(table_name: str):
    """Show column info and sample data for a table"""
    query = f"DESCRIBE TABLE {table_name}"
    print(f"\n=== Table Info: {table_name} ===")
    query_and_print_results(query)

# Main execution logic
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_sf.py '<query>' [format]")
        print("Formats: table (default), json, csv, describe")
        print("Special commands:")
        print("  - check:<table_name> - Quick data quality check")
        print("  - info:<table_name> - Show table structure")
        sys.exit(1)
    
    query = sys.argv[1]
    format_type = sys.argv[2] if len(sys.argv) > 2 else 'table'
    
    # Handle special commands
    if query.startswith('check:'):
        table_name = query.replace('check:', '')
        quick_check(table_name)
    elif query.startswith('info:'):
        table_name = query.replace('info:', '')
        show_table_info(table_name)
    else:
        # Regular query
        query_and_print_results(query, format_type)