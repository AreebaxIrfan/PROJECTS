import unittest
import os
import tempfile
from flask import Flask
from werkzeug.utils import secure_filename
from main import app, allowed_file  # Assuming your Flask app is saved as app.py

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create a temporary upload folder
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        # Sample form data for testing
        self.form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'linkedin': 'https://linkedin.com/in/johndoe',
            'website': 'https://johndoe.com',
            'intro': 'A passionate developer',
            'education[]': ['BSc Computer Science', 'MSc Data Science'],
            'experience[]': ['Software Engineer at XYZ', 'Data Analyst at ABC'],
            'skills[]': ['Python', 'JavaScript'],
            'languages[]': ['English', 'Spanish']
        }

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary upload folder and its contents
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_allowed_file(self):
        """Test the allowed_file function."""
        self.assertTrue(allowed_file('image.png'))
        self.assertTrue(allowed_file('image.jpg'))
        self.assertTrue(allowed_file('image.jpeg'))
        self.assertFalse(allowed_file('image.gif'))
        self.assertFalse(allowed_file('document.pdf'))

    def test_get_index(self):
        """Test GET request to index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)  # Check if HTML is returned
        self.assertIn(b'index.html', str(response.data))  # Check template usage indirectly

    def test_post_form_without_image(self):
        """Test POST request to index route without image."""
        response = self.client.post('/', data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'resume.html', str(response.data))  # Check if resume template is rendered
        self.assertIn(b'John Doe', response.data)  # Check if form data is present
        self.assertIn(b'john@example.com', response.data)
        self.assertIn(b'A passionate developer', response.data)

    def test_post_form_with_valid_image(self):
        """Test POST request to index route with a valid image."""
        # Create a temporary file to simulate image upload
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(b'\x89PNG\r\n\x1a\n')  # Minimal PNG header
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as image_file:
            data = self.form_data.copy()
            data['image'] = (image_file, 'test.png')
            response = self.client.post('/', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'resume.html', str(response.data))
        self.assertIn(b'John Doe', response.data)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, secure_filename('test.png'))))

        # Clean up temporary file
        os.remove(temp_file_path)

    def test_post_form_with_invalid_image(self):
        """Test POST request to index route with an invalid image."""
        # Create a temporary file to simulate invalid file upload
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4')  # Minimal PDF header
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as invalid_file:
            data = self.form_data.copy()
            data['image'] = (invalid_file, 'test.pdf')
            response = self.client.post('/', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'resume.html', str(response.data))
        self.assertIn(b'John Doe', response.data)
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, secure_filename('test.pdf'))))  # Invalid file not saved

        # Clean up temporary file
        os.remove(temp_file_path)

if __name__ == '__main__':
    unittest.main()