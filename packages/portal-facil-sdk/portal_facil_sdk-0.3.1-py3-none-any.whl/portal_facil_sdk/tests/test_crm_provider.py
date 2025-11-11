from datetime import datetime
from unittest import TestCase
from portal_facil_sdk.providers.crm_provider import Token



class TestToken(TestCase):
    
    def test_token_initialization(self):
        token_data = {
            'access_token': 'test_token',
            '.issued': 'Fri, 19 Sep 2025 16:31:05 GMT',
            '.expires': 'Fri, 03 Oct 2025 16:31:05 GMT'
        }
        token = Token(**token_data)
        self.assertEqual(token.access_token, 'test_token')
        self.assertEqual(
            token.expires_in, datetime.strptime(
                'Fri, 03 Oct 2025 16:31:05 GMT', 
                '%a, %d %b %Y %H:%M:%S %Z'
            )
        )
        self.assertTrue(token.is_expired)
    
    def test_token_expiration(self):
        token_data = {
            'access_token': 'test_token',
            '.issued': 'Fri, 19 Sep 2025 16:31:05 GMT',
            '.expires': 'Fri, 03 Oct 2025 16:31:05 GMT'
        }
        token = Token(**token_data)
        self.assertTrue(token.is_expired)