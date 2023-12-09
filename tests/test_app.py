import unittest
from app import app
from flask import json

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        # Zet de Flask-app op voor testing
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_home_page(self):
        # Test de homepagina
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_assistants(self):
        # Test het ophalen van assistenten
        response = self.app.get('/get_assistants')
        self.assertEqual(response.status_code, 200)

    def test_create_thread(self):
        # Test het aanmaken van een thread
        response = self.app.post('/create_thread', json={"data": "test data"})
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', json.loads(response.data))

    # Voeg hier meer tests toe voor andere routes en functionaliteiten

    # Voorbeeld voor het testen van error handling
    def test_error_handling(self):
        response = self.app.get('/niet_bestaande_route')
        self.assertEqual(response.status_code, 404)

    # Voorbeeld voor het testen van een POST-request met een fout
    def test_create_thread_with_error(self):
        response = self.app.post('/create_thread')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', json.loads(response.data))


if __name__ == '__main__':
    unittest.main()
