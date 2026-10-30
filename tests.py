"""Tests use ephemeral dictionaries; no invented observations are written to the dataset."""
import unittest
from datetime import date, timedelta
from database import validate_row


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.row = {'date': date.today().isoformat(), 'device': 'Phone',
                    'total_minutes': '90', 'social_minutes': '30',
                    'entertainment_minutes': '20', 'education_minutes': '10',
                    'productivity_minutes': '20', 'other_minutes': '10',
                    'pickups': '', 'day_type': 'College', 'focus_rating': ''}

    def test_valid_structure(self):
        result = validate_row(self.row)
        self.assertEqual(result['total_minutes'], 90)
        self.assertIsNone(result['pickups'])

    def test_mismatched_categories_rejected(self):
        self.row['social_minutes'] = '40'
        with self.assertRaises(ValueError):
            validate_row(self.row)

    def test_future_date_rejected(self):
        self.row['date'] = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            validate_row(self.row)

    def test_older_date_disallowed_for_new_entry(self):
        self.row['date'] = (date.today() - timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            validate_row(self.row, allow_prior_date=False)

    def test_bad_focus_rejected(self):
        self.row['focus_rating'] = '6'
        with self.assertRaises(ValueError):
            validate_row(self.row)


if __name__ == '__main__':
    unittest.main()
