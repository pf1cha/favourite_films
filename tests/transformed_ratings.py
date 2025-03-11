import unittest
from main import transform_ratings  # Replace your_module


class TestTransformRatings(unittest.TestCase):
    def test_valid_ratings(self):
        ratings_list = [
            {'Source': 'Internet Movie Database', 'Value': '8.8/10'},
            {'Source': 'Rotten Tomatoes', 'Value': '87%'},
            {'Source': 'Metacritic', 'Value': '74/100'}
        ]
        expected_result = {
            'Internet Movie Database': '88',
            'Rotten Tomatoes': '87',
            'Metacritic': '74'
        }
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_empty_ratings_list(self):
        ratings_list = []
        expected_result = {}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_none_ratings_list(self):
        ratings_list = None
        expected_result = {}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_missing_source(self):
        ratings_list = [
            {'Value': '8.8/10'},  # Missing 'Source'
            {'Source': 'Rotten Tomatoes', 'Value': '87%'}
        ]
        expected_result = {'Rotten Tomatoes': '87'}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_missing_value(self):
        ratings_list = [
            {'Source': 'Internet Movie Database', 'Value': '8.8/10'},
            {'Source': 'Rotten Tomatoes'}  # Missing 'Value'
        ]
        expected_result = {'Internet Movie Database': '88'}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_missing_both_keys(self):
        ratings_list = [
            {'Source': 'Internet Movie Database', 'Value': '8.8/10'},
            {'SomethingElse': 'SomethingElse'}  # Missing both 'Source' and 'Value'
        ]
        expected_result = {'Internet Movie Database': '88'}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_invalid_rating_entry_type(self):
        ratings_list = [
            {'Source': 'Internet Movie Database', 'Value': '8.8/10'},
            "invalid entry",  # Not a dictionary
            {'Source': 'Metacritic', 'Value': '74/100'}
        ]
        expected_result = {
            'Internet Movie Database': '88',
            'Metacritic': '74'
        }
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_ratings_with_only_text(self):
        ratings_list = [
            {'Source': 'Some Source', 'Value': 'No Score'}  # No digits
        ]
        expected_result = {'Some Source': ''}  # Empty string since no digits were found
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_ratings_with_mixed_text_and_numbers(self):
        ratings_list = [
            {'Source': 'Another Source', 'Value': 'A1B2C3D4'}
        ]
        expected_result = {'Another Source': '1234'}
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_ratings_with_leading_and_trailing_spaces(self):
        ratings_list = [
            {'Source': 'Leading Spaces', 'Value': '   90/100'},
            {'Source': 'Trailing Spaces', 'Value': '85%   '}
        ]
        expected_result = {
            'Leading Spaces': '90',
            'Trailing Spaces': '85'
        }
        self.assertEqual(transform_ratings(ratings_list), expected_result)

    def test_ratings_with_decimal(self):
        ratings_list = [
            {'Source': 'Decimal Source', 'Value': '9.5/10'},
        ]
        expected_result = {'Decimal Source': '95'}
        self.assertEqual(transform_ratings(ratings_list), expected_result)


if __name__ == '__main__':
    unittest.main()