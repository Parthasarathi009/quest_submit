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
        
    def load_bls_csv(self, file_path: str) -> pd.DataFrame:
        """Load BLS CSV file as DataFrame."""
        try:
            logger.info(f"Loading BLS data from {file_path}")
            df = pd.read_csv(file_path, sep='\t')
            logger.info(f"Loaded BLS data with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading BLS data: {e}")
            raise
    
    def load_bls_from_s3(self, s3_client, bucket: str, key: str) -> pd.DataFrame:
        """Load BLS CSV from S3."""
        try:
            logger.info(f"Loading BLS data from S3: s3://{bucket}/{key}")
            response = s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(io.BytesIO(response['Body'].read()), sep='\t')
            logger.info(f"Loaded BLS data with shape: {df.shape}")
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
            logger.info(f"Loaded population data with shape: {df.shape}")
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
            logger.info(f"Loaded population data with shape: {df.shape}")
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
            df: BLS DataFrame
            
        Returns:
            DataFrame with results
        """
        try:
            logger.info("Generating Report 2: Best Year per Series ID")
            
            # Strip whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()
            
            # Convert value to numeric
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Extract year from period if needed
            if 'year' not in df.columns and 'period' in df.columns:
                # Year might be embedded in period or another column
                logger.warning("Year column not found in BLS data")
            
            # Group by series_id and year, sum values
            yearly_sum = df.groupby(['series_id', 'year'])['value'].sum().reset_index()
            
            # Find best year (max value) for each series_id
            best_year = yearly_sum.loc[yearly_sum.groupby('series_id')['value'].idxmax()]
            best_year.columns = ['series_id', 'year', 'value']
            best_year = best_year.reset_index(drop=True)
            
            logger.info(f"Report 2 complete: {len(best_year)} series found")
            return best_year
            
        except Exception as e:
            logger.error(f"Error generating Report 2: {e}")
            raise
    
    def report_3_combined_analysis(self, bls_df: pd.DataFrame, pop_df: pd.DataFrame) -> pd.DataFrame:
        """
        Report 3: For series_id=PRS30006032 and period=Q01, show value and population.
        
        Args:
            bls_df: BLS DataFrame
            pop_df: Population DataFrame
            
        Returns:
            DataFrame with combined results
        """
        try:
            logger.info("Generating Report 3: Combined BLS and Population Analysis")
            
            # Strip whitespace
            for col in bls_df.select_dtypes(include=['object']).columns:
                bls_df[col] = bls_df[col].str.strip()
            
            for col in pop_df.select_dtypes(include=['object']).columns:
                pop_df[col] = pop_df[col].str.strip()
            
            # Filter BLS data
            filtered_bls = bls_df[
                (bls_df['series_id'] == 'PRS30006032') & 
                (bls_df['period'] == 'Q01')
            ].copy()
            
            # Convert columns to numeric
            filtered_bls['value'] = pd.to_numeric(filtered_bls['value'], errors='coerce')
            filtered_bls['year'] = pd.to_numeric(filtered_bls['year'], errors='coerce')
            
            # Normalize population dataframe
            pop_df_copy = pop_df.copy()
            if 'Year' in pop_df_copy.columns:
                pop_df_copy['year'] = pd.to_numeric(pop_df_copy['Year'], errors='coerce')
            
            if 'Population' in pop_df_copy.columns:
                pop_df_copy['population'] = pd.to_numeric(pop_df_copy['Population'], errors='coerce')
                pop_col = 'population'
            else:
                pop_cols = [col for col in pop_df_copy.columns if 'population' in col.lower()]
                if pop_cols:
                    pop_df_copy['population'] = pd.to_numeric(pop_df_copy[pop_cols[0]], errors='coerce')
                    pop_col = 'population'
                else:
                    pop_col = None
            
            # Merge on year
            if pop_col:
                result = filtered_bls.merge(
                    pop_df_copy[['year', pop_col]],
                    on='year',
                    how='left'
                )
                result = result[['series_id', 'year', 'period', 'value', pop_col]]
                result.columns = ['series_id', 'year', 'period', 'value', 'Population']
            else:
                result = filtered_bls[['series_id', 'year', 'period', 'value']]
            
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


def generate_all_reports(bls_data_path: str, population_data_path: str, output_dir: str = "."):
    """Generate all reports and save outputs."""
    try:
        analytics = DataAnalytics()
        
        # Load data
        bls_df = analytics.load_bls_csv(bls_data_path)
        pop_df = analytics.load_population_json(population_data_path)
        
        # Generate reports
        report_1 = analytics.report_1_population_stats(pop_df)
        report_2 = analytics.report_2_best_year_per_series(bls_df)
        report_3 = analytics.report_3_combined_analysis(bls_df, pop_df)
        
        # Save reports
        logger.info(f"Report 1: {report_1}")
        
        analytics.save_report_to_csv(report_2, f"{output_dir}/report_2_best_year.csv")
        analytics.save_report_to_csv(report_3, f"{output_dir}/report_3_combined.csv")
        
        logger.info("All reports generated successfully")
        return {
            'report_1': report_1,
            'report_2': report_2,
            'report_3': report_3
        }
        
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        raise


if __name__ == "__main__":
    # Example usage - adjust paths as needed
    import sys
    
    if len(sys.argv) > 2:
        bls_path = sys.argv[1]
        pop_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else "."
        generate_all_reports(bls_path, pop_path, output_path)
    else:
        print("Usage: python analytics.py <bls_csv_path> <population_json_path> [output_dir]")
