"""
Unit tests for Part 2: Population API
"""

import unittest
from unittest.mock import patch, MagicMock
from part_2_api.fetch_population_data import PopulationDataFetcher
import json


class TestPopulationDataFetcher(unittest.TestCase):
    """Test cases for PopulationDataFetcher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bucket_name = "test-bucket"
        self.fetcher = PopulationDataFetcher(self.bucket_name)
    
    @patch('part_2_api.fetch_population_data.requests.get')
    def test_fetch_population_data(self, mock_get):
        """Test fetching data from API"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'Year': 2018, 'Population': 327167439}
            ]
        }
        mock_get.return_value = mock_response
        
        data = self.fetcher.fetch_population_data()
        
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['Year'], 2018)
    
    @patch('part_2_api.fetch_population_data.boto3.client')
    def test_save_to_s3(self, mock_boto):
        """Test saving data to S3"""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        fetcher = PopulationDataFetcher(self.bucket_name)
        data = {'data': [{'Year': 2018, 'Population': 327167439}]}
        
        result = fetcher.save_to_s3(data)
        
        # Verify S3 put_object was called
        self.assertTrue(mock_s3.put_object.called)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
