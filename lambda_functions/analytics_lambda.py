"""
Lambda Function for Part 3 Analytics
This lambda is triggered by SQS messages from S3 notifications and generates reports.
"""

import sys
import os
import json
import logging
import boto3
from datetime import datetime
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from part_3_analytics.analytics import DataAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

S3_BUCKET = os.environ.get("S3_BUCKET", "rearc-quest-data")
s3_client = boto3.client('s3')


def generate_reports_from_s3():
    """Generate analytics reports using data from S3."""
    try:
        logger.info("Generating analytics reports from S3 data")
        
        analytics = DataAnalytics()
        
        # Load data from S3
        bls_df = analytics.load_bls_from_s3(s3_client, S3_BUCKET, "bls_time_series/pr.data.0.Current")
        pop_df = analytics.load_population_from_s3(s3_client, S3_BUCKET, "population_data/population_data.json")
        
        # Generate reports
        logger.info("Generating Report 1: Population Statistics")
        report_1 = analytics.report_1_population_stats(pop_df)
        logger.info(f"Report 1 Results: {json.dumps(report_1, indent=2)}")
        
        logger.info("Generating Report 2: Best Year per Series")
        report_2 = analytics.report_2_best_year_per_series(bls_df)
        logger.info(f"Report 2 Results (first 10 rows):\n{report_2.head(10).to_string()}")
        
        logger.info("Generating Report 3: Combined Analysis")
        report_3 = analytics.report_3_combined_analysis(bls_df, pop_df)
        logger.info(f"Report 3 Results:\n{report_3.to_string()}")
        
        return {
            'report_1': report_1,
            'report_2_rows': len(report_2),
            'report_3_rows': len(report_3),
            'all_reports': {
                'report_1': report_1,
                'report_2': report_2.to_dict('records'),
                'report_3': report_3.to_dict('records')
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating reports: {e}", exc_info=True)
        raise


def lambda_handler(event, context):
    """
    Lambda handler for SQS-triggered analytics.
    Processes messages from SQS queue and generates reports.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'processed_messages': 0,
        'reports': []
    }
    
    try:
        # Process each message from SQS
        records = event.get('Records', [])
        
        for record in records:
            logger.info(f"Processing message: {record['messageId']}")
            
            try:
                # Generate reports
                report_results = generate_reports_from_s3()
                results['reports'].append(report_results)
                results['processed_messages'] += 1
                
                logger.info(f"Successfully processed message {record['messageId']}")
                
            except Exception as e:
                logger.error(f"Error processing message {record['messageId']}: {e}")
                results['reports'].append({
                    'error': str(e),
                    'messageId': record['messageId']
                })
        
        logger.info(f"All messages processed. Processed: {results['processed_messages']}/{len(records)}")
        
        return {
            'statusCode': 200 if results['processed_messages'] > 0 else 204,
            'body': json.dumps(results, indent=2, default=str)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


if __name__ == "__main__":
    # For local testing
    test_event = {
        'Records': [
            {
                'messageId': 'test-message-1',
                'body': 'Test message'
            }
        ]
    }
    result = lambda_handler(test_event, {})
    print(json.dumps(result, indent=2))
