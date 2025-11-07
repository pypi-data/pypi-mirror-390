"""Tests for FlaskIt routing system."""
import unittest
from flaskit import FlaskIt, Route


class TestRouting(unittest.TestCase):
    """Test FlaskIt routing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = FlaskIt(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_route_creation(self):
        """Test that routes can be created."""
        route = Route()
        self.assertIsNotNone(route)
    
    def test_view_route(self):
        """Test view route registration."""
        route = Route()
        route.view('/', 'home.index').name('home')
        self.assertEqual(len(route._routes), 1)
    
    def test_get_route(self):
        """Test GET route registration."""
        def handler():
            return {'message': 'Hello'}
        
        route = Route()
        route.get('/api/test', handler).name('api.test')
        self.assertEqual(len(route._routes), 1)
    
    def test_route_naming(self):
        """Test route naming."""
        route = Route()
        route.view('/', 'home.index').name('home')
        self.assertEqual(route._routes[0]['name'], 'home')
    
    def test_route_group(self):
        """Test route grouping."""
        route = Route()
        with route.group('/admin'):
            route.view('/dashboard', 'admin.dashboard')
        
        self.assertEqual(len(route._routes), 1)


if __name__ == '__main__':
    unittest.main()
