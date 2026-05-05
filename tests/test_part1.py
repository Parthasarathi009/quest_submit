"""
Unit tests for Part 1: BLS Data Sync
"""

import unittest
from unittest.mock import patch, MagicMock
from part_1_s3_sync.sync_bls_data import BLSDataSync
import hashlib


class TestBLSDataSync(unittest.TestCase):
    """Test cases for BLSDataSync class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bucket_name = "test-bucket"
        self.syncer = BLSDataSync(self.bucket_name)
    
    @patch('part_1_s3_sync.sync_bls_data.requests.get')
    def test_get_remote_file_list(self, mock_get):
        """Test fetching file list from BLS"""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <a href="pr.data.0.Current">pr.data.0.Current</a>
            <a href="pr.txt">pr.txt</a>
        </html>
        '''
        mock_get.return_value = mock_response
        
        files = self.syncer.get_remote_file_list()
        
        self.assertIn('pr.data.0.Current', files)
        self.assertIn('pr.txt', files)
    
    @patch('part_1_s3_sync.sync_bls_data.requests.get')
    def test_get_file_hash(self, mock_get):
        """Test file hash computation"""
        mock_response = MagicMock()
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        file_hash = self.syncer.get_file_hash("http://test.com/file")
        
        expected_hash = hashlib.md5(b"test content").hexdigest()
        self.assertEqual(file_hash, expected_hash)
    
    @patch('part_1_s3_sync.sync_bls_data.boto3.client')
    def test_upload_file_to_s3(self, mock_boto):
        """Test S3 upload"""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        with patch('part_1_s3_sync.sync_bls_data.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"test data"
            mock_get.return_value = mock_response
            
            syncer = BLSDataSync(self.bucket_name)
            result = syncer.upload_file_to_s3("http://test.com/file", "test.txt")
            
            # Verify S3 put_object was called
            self.assertTrue(mock_s3.put_object.called)


if __name__ == '__main__':
    unittest.main()
