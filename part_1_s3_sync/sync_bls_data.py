"""
Part 1: AWS S3 & Sourcing Datasets
Syncs BLS time series data to S3, keeping it up-to-date with the source.
"""

import os
import boto3
import requests
from datetime import datetime
import logging
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BLS_BASE_URL = "https://download.bls.gov/pub/time.series/pr/"
S3_BUCKET = os.environ.get("S3_BUCKET", "rearc-quest-data")
S3_PREFIX = "bls_time_series"

# User-Agent header for BLS compliance
HEADERS = {
    "User-Agent": "contact@yourcompany.com"  # Replace with your contact info
}


class BLSDataSync:
    """Handles syncing BLS data to S3."""
    
    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket = bucket_name
        self.synced_files = {}
        
    def get_remote_file_list(self) -> dict:
        """
        Fetch the list of files from BLS server.
        Returns a dictionary mapping filename to file info.
        """
        try:
            response = requests.get(BLS_BASE_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            files = {}
            # Parse HTML to extract file links
            from html.parser import HTMLParser
            
            class LinkParser(HTMLParser):
                def handle_starttag(self, tag, attrs):
                    if tag == 'a':
                        for attr, value in attrs:
                            if attr == 'href' and value and not value.startswith('/'):
                                if value not in ['..', '../']:
                                    files[value] = {'name': value}
            
            parser = LinkParser()
            parser.feed(response.text)
            
            logger.info(f"Found {len(files)} files on BLS server")
            return files
            
        except Exception as e:
            logger.error(f"Error fetching file list from BLS: {e}")
            raise
    
    def get_file_hash(self, file_url: str) -> str:
        """Download file and compute its hash for comparison."""
        try:
            response = requests.get(file_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return hashlib.md5(response.content).hexdigest()
        except Exception as e:
            logger.error(f"Error downloading file {file_url}: {e}")
            return None
    
    def get_s3_file_hash(self, s3_key: str) -> str:
        """Get hash of file already in S3."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            # Check if metadata contains hash
            if 'Metadata' in response and 'file-hash' in response['Metadata']:
                return response['Metadata']['file-hash']
            return None
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            logger.warning(f"Error getting S3 file hash for {s3_key}: {e}")
            return None
    
    def upload_file_to_s3(self, file_url: str, filename: str) -> bool:
        """Download and upload a single file to S3."""
        try:
            response = requests.get(file_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            file_hash = hashlib.md5(response.content).hexdigest()
            s3_key = f"{S3_PREFIX}/{filename}"
            
            # Check if file already exists with same hash
            existing_hash = self.get_s3_file_hash(s3_key)
            if existing_hash == file_hash:
                logger.info(f"File {filename} unchanged, skipping upload")
                return False
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=response.content,
                Metadata={'file-hash': file_hash, 'sync-date': datetime.now().isoformat()}
            )
            logger.info(f"Successfully uploaded {filename} to S3")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading {filename} to S3: {e}")
            return False
    
    def delete_removed_files(self, current_files: set):
        """Delete files from S3 that no longer exist on BLS."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=S3_PREFIX
            )
            
            if 'Contents' not in response:
                logger.info("No files in S3 to check for deletion")
                return
            
            for obj in response['Contents']:
                s3_key = obj['Key']
                filename = s3_key.replace(f"{S3_PREFIX}/", "")
                
                if filename not in current_files and filename:
                    self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
                    logger.info(f"Deleted {filename} from S3 (no longer on BLS server)")
                    
        except Exception as e:
            logger.error(f"Error deleting removed files: {e}")
    
    def sync(self):
        """Execute the full sync operation."""
        logger.info("Starting BLS data sync...")
        
        try:
            # Ensure S3 bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket)
                logger.info(f"S3 bucket {self.bucket} exists")
            except self.s3_client.exceptions.NoSuchBucket:
                logger.info(f"Creating S3 bucket {self.bucket}")
                self.s3_client.create_bucket(Bucket=self.bucket)
            
            # Get list of files from BLS
            remote_files = self.get_remote_file_list()
            current_files = set(remote_files.keys())
            
            uploaded_count = 0
            for filename in current_files:
                file_url = f"{BLS_BASE_URL}{filename}"
                if self.upload_file_to_s3(file_url, filename):
                    uploaded_count += 1
            
            # Delete files that are no longer on BLS
            self.delete_removed_files(current_files)
            
            logger.info(f"Sync complete. Uploaded {uploaded_count} new/updated files")
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False


def lambda_handler(event, context):
    """Lambda handler for scheduled sync."""
    try:
        syncer = BLSDataSync(S3_BUCKET)
        success = syncer.sync()
        return {
            'statusCode': 200 if success else 500,
            'body': 'Sync completed successfully' if success else 'Sync failed'
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


if __name__ == "__main__":
    # For local testing
    syncer = BLSDataSync(S3_BUCKET)
    syncer.sync()
