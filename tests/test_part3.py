"""
Unit tests for Part 3: Analytics
"""

import unittest
import pandas as pd
from part_3_analytics.analytics import DataAnalytics


class TestDataAnalytics(unittest.TestCase):
    """Test cases for DataAnalytics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analytics = DataAnalytics()
        
        # Create sample BLS data
        self.bls_data = pd.DataFrame({
            'series_id': ['PRS30006011', 'PRS30006011', 'PRS30006011', 'PRS30006011',
                          'PRS30006012', 'PRS30006012', 'PRS30006012', 'PRS30006012'],
            'year': [1995, 1995, 1996, 1996, 2000, 2000, 2001, 2001],
            'period': ['Q01', 'Q02', 'Q01', 'Q02', 'Q01', 'Q02', 'Q01', 'Q02'],
            'value': [1, 2, 3, 4, 0, 8, 2, 3]
        })
        
        # Create sample population data
        self.population_data = pd.DataFrame({
            'Year': [2013, 2014, 2015, 2016, 2017, 2018],
            'Population': [315005716, 317297725, 319297384, 322999999, 325084756, 327167439]
        })
    
    def test_report_1_population_stats(self):
        """Test population statistics report"""
        result = self.analytics.report_1_population_stats(self.population_data)
        
        self.assertIn('mean_population', result)
        self.assertIn('std_deviation', result)
        self.assertGreater(result['mean_population'], 0)
        self.assertGreater(result['std_deviation'], 0)
    
    def test_report_2_best_year_per_series(self):
        """Test best year per series report"""
        result = self.analytics.report_2_best_year_per_series(self.bls_data)
        
        self.assertEqual(len(result), 2)
        # PRS30006011 best year should be 1996 (7 vs 3)
        row1 = result[result['series_id'] == 'PRS30006011'].iloc[0]
        self.assertEqual(row1['year'], 1996)
        self.assertEqual(row1['value'], 7)
    
    def test_report_3_combined_analysis(self):
        """Test combined analysis report"""
        # Add PRS30006032 to test data
        bls_data_extended = self.bls_data.copy()
        bls_data_extended = pd.concat([
            bls_data_extended,
            pd.DataFrame({
                'series_id': ['PRS30006032', 'PRS30006032'],
                'year': [2018, 2018],
                'period': ['Q01', 'Q02'],
                'value': [1.9, 2.0]
            })
        ], ignore_index=True)
        
        result = self.analytics.report_3_combined_analysis(bls_data_extended, self.population_data)
        
        # Should have at least one row
        self.assertGreaterEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
