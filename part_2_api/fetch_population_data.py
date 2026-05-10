"""
Part 2: DataUSA Population API
Fetches US population data and saves it to S3 as JSON.
"""

import os
import boto3
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords"
PARAMS = {
    "cube": "acs_yg_total_population_1",
    "drilldowns": "Year,Nation",
    "locale": "en",
    "measures": "Population"
}

S3_BUCKET = os.environ.get("S3_BUCKET", "parth-rearc-quest-data-2026")
S3_KEY = "population_data/population_data.json"

HEADERS = {
    "User-Agent": "parthasarathi.samantaray87@gmail.com"  # Replace with your contact info
}


class PopulationDataFetcher:
    """Handles fetching population data from DataUSA API and saving to S3."""
    
    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket = bucket_name
        
    def fetch_population_data(self) -> Dict[str, Any]:
        """
        Fetch population data from DataUSA API.
        
        Returns:
            Dictionary containing the API response data
        """
        try:
            logger.info(f"Fetching data from API: {API_URL}")
            response = requests.get(
                API_URL,
                params=PARAMS,
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched data. Records: {len(data.get('data', []))}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            raise
    
    def save_to_s3(self, data: Dict[str, Any]) -> bool:
        """
        Save JSON data to S3.
        
        Args:
            data: Dictionary to save as JSON
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure S3 bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket)
                logger.info(f"S3 bucket {self.bucket} exists")
            except self.s3_client.exceptions.NoSuchBucket:
                logger.info(f"Creating S3 bucket {self.bucket}")
                self.s3_client.create_bucket(Bucket=self.bucket)
            
            # Add metadata to the data
            data_with_metadata = {
                'data': data.get('data', []),
                'metadata': {
                    'fetched_at': datetime.now().isoformat(),
                    'api_url': API_URL,
                    'parameters': PARAMS
                }
            }
            
            # Convert to JSON
            json_data = json.dumps(data_with_metadata, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=S3_KEY,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                Metadata={'fetched-date': datetime.now().isoformat()}
            )
            
            logger.info(f"Successfully saved data to s3://{self.bucket}/{S3_KEY}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to S3: {e}")
            return False
    
    def save_locally(self, data: Dict[str, Any], filename: str = "population_data.json") -> bool:
        """
        Save JSON data locally as fallback when S3 fails.
        
        Args:
            data: Dictionary to save as JSON
            filename: Local filename to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata to the data
            data_with_metadata = {
                'data': data.get('data', []),
                'metadata': {
                    'fetched_at': datetime.now().isoformat(),
                    'api_url': API_URL,
                    'parameters': PARAMS,
                    'saved_locally': True
                }
            }
            
            # Save to local file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_with_metadata, f, indent=2)
            
            logger.info(f"Successfully saved data locally to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data locally: {e}")
            return False
    
    def fetch_and_save(self) -> bool:
        """
        Fetch data from API and save to S3, with local fallback.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.fetch_population_data()
            
            # Try S3 first
            if self.save_to_s3(data):
                return True
            
            # Fallback to local save
            logger.warning("S3 save failed, saving locally instead")
            return self.save_locally(data)
            
        except Exception as e:
            logger.error(f"Fetch and save operation failed: {e}")
            return False


def lambda_handler(event, context):
    """Lambda handler for scheduled API fetch."""
    try:
        fetcher = PopulationDataFetcher(S3_BUCKET)
        success = fetcher.fetch_and_save()
        
        return {
            'statusCode': 200 if success else 500,
            'body': json.dumps({
                'message': 'Population data fetched and saved successfully' if success else 'Failed to fetch/save data',
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


if __name__ == "__main__":
    # For local testing
    fetcher = PopulationDataFetcher(S3_BUCKET)
    fetcher.fetch_and_save()
