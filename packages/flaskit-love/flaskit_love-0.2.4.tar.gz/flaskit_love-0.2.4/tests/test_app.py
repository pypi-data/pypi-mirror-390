"""Tests for FlaskIt core application."""
import unittest
from flaskit import FlaskIt


class TestFlaskItApp(unittest.TestCase):
    """Test FlaskIt application initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = FlaskIt(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_app_creation(self):
        """Test that FlaskIt app can be created."""
        self.assertIsNotNone(self.app)
        self.assertIsInstance(self.app, FlaskIt)
    
    def test_app_name(self):
        """Test that app name is set correctly."""
        self.assertEqual(self.app.name, __name__)
    
    def test_testing_mode(self):
        """Test that testing mode can be enabled."""
        self.assertTrue(self.app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()
