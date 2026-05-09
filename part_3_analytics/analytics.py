"""
Part 3: Data Analytics
Generates reports from BLS and population data using Spark/Pandas.
"""

import pandas as pd
import json
import logging
from datetime import datetime
from typing import Tuple
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataAnalytics:
    """Handles data analytics and reporting."""
    
    def __init__(self):
        self.bls_data = None
        self.population_data = None
    
    def clean_bls_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean BLS DataFrame: strip whitespace, convert types, handle data quality issues.
        
        Args:
            df: Raw BLS DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info("Cleaning BLS data...")
            
            # Clean column names (remove leading/trailing whitespace)
            df.columns = df.columns.str.strip()
            
            # Clean string columns (remove leading/trailing whitespace from values)
            string_columns = ['series_id', 'period', 'footnote_codes']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            
            # Convert numeric columns
            if 'year' in df.columns:
                df['year'] = pd.to_numeric(df['year'], errors='coerce')
            
            if 'value' in df.columns:
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['series_id', 'year', 'period'])
            
            logger.info(f"BLS data cleaned: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning BLS data: {e}")
            raise
    
    def clean_population_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean Population DataFrame: normalize column names, convert types.
        
        Args:
            df: Raw Population DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info("Cleaning population data...")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Clean string columns
            string_columns = ['Nation', 'Year']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            
            # Convert numeric columns
            if 'Year' in df.columns:
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            
            if 'Population' in df.columns:
                df['Population'] = pd.to_numeric(df['Population'], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['Year'])
            
            logger.info(f"Population data cleaned: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning population data: {e}")
            raise
        
    def load_bls_csv(self, file_path: str) -> pd.DataFrame:
        """Load BLS CSV file as DataFrame."""
        try:
            logger.info(f"Loading BLS data from {file_path}")
            df = pd.read_csv(file_path, sep='\t', dtype=str)  # Load as strings first
            df = self.clean_bls_data(df)  # Clean the data
            logger.info(f"Loaded and cleaned BLS data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading BLS data: {e}")
            raise
    
    def load_bls_from_s3(self, s3_client, bucket: str, key: str) -> pd.DataFrame:
        """Load BLS CSV from S3."""
        try:
            logger.info(f"Loading BLS data from S3: s3://{bucket}/{key}")
            response = s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(io.BytesIO(response['Body'].read()), sep='\t', dtype=str)
            df = self.clean_bls_data(df)  # Clean the data
            logger.info(f"Loaded and cleaned BLS data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading BLS data from S3: {e}")
            raise
    
    def load_population_json(self, file_path: str) -> pd.DataFrame:
        """Load population JSON file as DataFrame."""
        try:
            logger.info(f"Loading population data from {file_path}")
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract the data records
            records = data.get('data', []) if isinstance(data, dict) else data
            df = pd.DataFrame(records)
            df = self.clean_population_data(df)  # Clean the data
            logger.info(f"Loaded and cleaned population data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading population data: {e}")
            raise
    
    def load_population_from_s3(self, s3_client, bucket: str, key: str) -> pd.DataFrame:
        """Load population JSON from S3."""
        try:
            logger.info(f"Loading population data from S3: s3://{bucket}/{key}")
            response = s3_client.get_object(Bucket=bucket, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Extract the data records
            records = data.get('data', []) if isinstance(data, dict) else data
            df = pd.DataFrame(records)
            df = self.clean_population_data(df)  # Clean the data
            logger.info(f"Loaded and cleaned population data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading population data from S3: {e}")
            raise
    
    def report_1_population_stats(self, df: pd.DataFrame) -> dict:
        """
        Report 1: Generate mean and standard deviation of US population [2013-2018].
        
        Args:
            df: Population DataFrame
            
        Returns:
            Dictionary with statistics
        """
        try:
            logger.info("Generating Report 1: Population Statistics (2013-2018)")
            
            # Convert Year to numeric if needed
            if 'Year' in df.columns:
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            
            # Filter for years 2013-2018
            filtered_df = df[(df['Year'] >= 2013) & (df['Year'] <= 2018)]
            
            if 'Population' in df.columns:
                population_col = 'Population'
            else:
                # Try to find population column
                population_col = [col for col in df.columns if 'population' in col.lower()][0]
            
            filtered_df[population_col] = pd.to_numeric(filtered_df[population_col], errors='coerce')
            
            mean_pop = filtered_df[population_col].mean()
            std_pop = filtered_df[population_col].std()
            
            result = {
                'report_name': 'Population Statistics (2013-2018)',
                'mean_population': round(mean_pop, 2),
                'std_deviation': round(std_pop, 2),
                'years_covered': '2013-2018',
                'records_used': len(filtered_df)
            }
            
            logger.info(f"Report 1 complete: Mean={result['mean_population']}, StdDev={result['std_deviation']}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Report 1: {e}")
            raise
    
    def report_2_best_year_per_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Report 2: For each series_id, find the best year (max sum of values per year).
        
        Args:
            df: BLS DataFrame (already cleaned)
            
        Returns:
            DataFrame with results
        """
        try:
            logger.info("Generating Report 2: Best Year per Series ID")
            
            # Data is already cleaned, just ensure proper types
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            
            # Group by series_id and year, sum values
            yearly_sum = df.groupby(['series_id', 'year'])['value'].sum().reset_index()
            
            # Find best year (max value) for each series_id
            best_year = yearly_sum.loc[yearly_sum.groupby('series_id')['value'].idxmax()]
            best_year.columns = ['series_id', 'year', 'value']
            best_year = best_year.reset_index(drop=True)
            
            # Round values to 2 decimal places
            best_year['value'] = best_year['value'].round(2)
            
            logger.info(f"Report 2 complete: {len(best_year)} series found")
            return best_year
            
        except Exception as e:
            logger.error(f"Error generating Report 2: {e}")
            raise
    
    def report_3_combined_analysis(self, bls_df: pd.DataFrame, pop_df: pd.DataFrame) -> pd.DataFrame:
        """
        Report 3: For series_id=PRS30006032 and period=Q01, show value and population.
        
        Args:
            bls_df: BLS DataFrame (already cleaned)
            pop_df: Population DataFrame (already cleaned)
            
        Returns:
            DataFrame with combined results
        """
        try:
            logger.info("Generating Report 3: Combined BLS and Population Analysis")
            
            # Data is already cleaned, just ensure proper types
            bls_df['value'] = pd.to_numeric(bls_df['value'], errors='coerce')
            bls_df['year'] = pd.to_numeric(bls_df['year'], errors='coerce')
            pop_df['Year'] = pd.to_numeric(pop_df['Year'], errors='coerce')
            pop_df['Population'] = pd.to_numeric(pop_df['Population'], errors='coerce')
            
            # Filter BLS data
            filtered_bls = bls_df[
                (bls_df['series_id'] == 'PRS30006032') & 
                (bls_df['period'] == 'Q01')
            ].copy()
            
            # Normalize population dataframe for merging
            pop_df_copy = pop_df.copy()
            pop_df_copy['year'] = pop_df_copy['Year']  # Create year column for merging
            
            # Merge on year
            result = filtered_bls.merge(
                pop_df_copy[['year', 'Population']],
                on='year',
                how='left'
            )
            result = result[['series_id', 'year', 'period', 'value', 'Population']]
            
            # Round values to 2 decimal places
            result['value'] = result['value'].round(2)
            
            logger.info(f"Report 3 complete: {len(result)} records found")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Report 3: {e}")
            raise
    
    def save_report_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save report DataFrame to CSV."""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Saved report to {output_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise


def generate_all_reports_s3(s3_bucket: str, output_dir: str = "."):
    """Generate all reports using data from S3."""
    try:
        import boto3
        s3_client = boto3.client('s3')
        
        analytics = DataAnalytics()
        
        # Load data from S3
        bls_df = analytics.load_bls_from_s3(s3_client, s3_bucket, "bls_time_series/pr.data.0.Current")
        pop_df = analytics.load_population_from_s3(s3_client, s3_bucket, "population_data/population_data.json")
        
        # Generate reports
        report_1 = analytics.report_1_population_stats(pop_df)
        report_2 = analytics.report_2_best_year_per_series(bls_df)
        report_3 = analytics.report_3_combined_analysis(bls_df, pop_df)
        
        # Save reports
        logger.info(f"Report 1: {report_1}")
        
        analytics.save_report_to_csv(report_2, f"{output_dir}/report_2_best_year.csv")
        analytics.save_report_to_csv(report_3, f"{output_dir}/report_3_combined.csv")
        
        logger.info("All reports generated successfully from S3 data")
        return {
            'report_1': report_1,
            'report_2': report_2,
            'report_3': report_3
        }
        
    except Exception as e:
        logger.error(f"Error generating reports from S3: {e}")
        raise


if __name__ == "__main__":
    # Example usage - adjust paths as needed
    import sys
    
    if len(sys.argv) > 1:
        # Use S3 bucket from command line
        s3_bucket = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "."
        generate_all_reports_s3(s3_bucket, output_path)
    else:
        # Default S3 bucket
        s3_bucket = "parth-rearc-quest-data-2026"
        output_path = "."
        
        print(f"Using default S3 bucket: {s3_bucket}")
        print(f"Output directory: {output_path}")
        
        try:
            generate_all_reports_s3(s3_bucket, output_path)
        except FileNotFoundError as e:
            print(f"S3 data not found: {e}")
            print("Make sure Part 1 and Part 2 have uploaded data to S3")
            print("Usage: python analytics.py <s3_bucket_name> [output_dir]")
        except Exception as e:
            print(f"Error: {e}")
            print("Usage: python analytics.py <s3_bucket_name> [output_dir]")
