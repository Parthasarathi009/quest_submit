"""
Combined Lambda Function for Part 1 and Part 2
This lambda is triggered daily via EventBridge and runs both BLS sync and population API fetch.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from part_1_s3_sync.sync_bls_data import BLSDataSync
from part_2_api.fetch_population_data import PopulationDataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

S3_BUCKET = os.environ.get("S3_BUCKET", "rearc-quest-data")


def lambda_handler(event, context):
    """
    Lambda handler for daily scheduled execution.
    Executes both Part 1 (BLS sync) and Part 2 (population API fetch).
    """
    logger.info("Starting combined data pipeline...")
    results = {
        'timestamp': datetime.now().isoformat(),
        'part_1_bls_sync': None,
        'part_2_population_api': None
    }
    
    try:
        # Part 1: Sync BLS data
        logger.info("Starting Part 1: BLS data sync")
        syncer = BLSDataSync(S3_BUCKET)
        bls_success = syncer.sync()
        results['part_1_bls_sync'] = {
            'success': bls_success,
            'status': 'Completed' if bls_success else 'Failed'
        }
        
    except Exception as e:
        logger.error(f"Part 1 failed: {e}")
        results['part_1_bls_sync'] = {
            'success': False,
            'status': f'Error: {str(e)}'
        }
    
    try:
        # Part 2: Fetch population data
        logger.info("Starting Part 2: Population data fetch")
        fetcher = PopulationDataFetcher(S3_BUCKET)
        pop_success = fetcher.fetch_and_save()
        results['part_2_population_api'] = {
            'success': pop_success,
            'status': 'Completed' if pop_success else 'Failed'
        }
        
    except Exception as e:
        logger.error(f"Part 2 failed: {e}")
        results['part_2_population_api'] = {
            'success': False,
            'status': f'Error: {str(e)}'
        }
    
    # Determine overall status
    all_success = (
        results['part_1_bls_sync'].get('success', False) and
        results['part_2_population_api'].get('success', False)
    )
    
    logger.info(f"Pipeline execution complete: {json.dumps(results, indent=2)}")
    
    return {
        'statusCode': 200 if all_success else 500,
        'body': json.dumps(results, indent=2)
    }


if __name__ == "__main__":
    # For local testing
    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
