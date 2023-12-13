import unittest
from unittest.mock import patch, Mock
from demo_service_rest_backend.lambda_function import lambda_handler
from demo_service_rest_backend.utils import log_request_received, call_api

class TestLambdaHandler(unittest.TestCase):

    @patch('demo_service_rest_backend.lambda_function.call_api')
    def test_lambda_handler_get_customer_profile_success(self, mock_call_api):
        
        mock_response = Mock()
        # Mock the first call_api function to return a 200 response
        mock_call_api.return_value = [
            200, '{"performActionImplemented": {"enabled":"true"}}', {'Content-Type': 'application/json'}
        ]

        # Create a sample event
        event = {
            'version': '2.0',
            'routeKey': '$default',
            'rawPath': '/address',
            'rawQueryString': 'methodToCall=GetCustomerProfile&phoneNumber=1234',
            'headers': {
                # Your headers here
            },
            'queryStringParameters': {
                'methodToCall': 'GetCustomerProfile',
                'phoneNumber': 1234
            },
            'requestContext': {
                # Your request context here
            },
            'isBase64Encoded': False
        }

        # Call the lambda_handler function
        response = lambda_handler(event, None)

        # Assertions for the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"performActionImplemented": {"enabled":"true"}}')
        self.assertEqual(response['headers'], {'Content-Type': 'application/json'})

if __name__ == '__main__':
    unittest.main()
