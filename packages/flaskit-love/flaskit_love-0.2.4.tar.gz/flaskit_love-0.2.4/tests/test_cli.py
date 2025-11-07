"""Tests for FlaskIt CLI commands."""
import unittest
import os
import shutil
from click.testing import CliRunner
from flaskit.cli import cli


class TestCLI(unittest.TestCase):
    """Test FlaskIt CLI commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_project = 'test_project'
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_project):
            shutil.rmtree(self.test_project)
    
    def test_cli_exists(self):
        """Test that CLI is accessible."""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
    
    def test_new_command_creates_project(self):
        """Test that 'new' command creates a project."""
        result = self.runner.invoke(cli, ['new', self.test_project])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.test_project))
    
    def test_new_command_creates_structure(self):
        """Test that 'new' command creates correct structure."""
        self.runner.invoke(cli, ['new', self.test_project])
        
        # Check main folders
        self.assertTrue(os.path.exists(f'{self.test_project}/app'))
        self.assertTrue(os.path.exists(f'{self.test_project}/routes'))
        self.assertTrue(os.path.exists(f'{self.test_project}/web'))
        
        # Check app subfolders
        self.assertTrue(os.path.exists(f'{self.test_project}/app/models'))
        self.assertTrue(os.path.exists(f'{self.test_project}/app/logics'))
        self.assertTrue(os.path.exists(f'{self.test_project}/app/services'))
        self.assertTrue(os.path.exists(f'{self.test_project}/app/config'))
        self.assertTrue(os.path.exists(f'{self.test_project}/app/middlewares'))
        
        # Check main files
        self.assertTrue(os.path.exists(f'{self.test_project}/app.py'))
        self.assertTrue(os.path.exists(f'{self.test_project}/requirements.txt'))


if __name__ == '__main__':
    unittest.main()
