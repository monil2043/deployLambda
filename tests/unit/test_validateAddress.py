import unittest
from unittest.mock import patch, Mock
from demo_service_rest_backend.lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('demo_service_rest_backend.lambda_function.call_api')
    def test_lambda_handler_with_valid_input(self, mock_call_api):
        event = {
  'version': '2.0',
  'routeKey': '$default',
  'rawPath': '/address',
  'rawQueryString': 'address1=SUITE%20K&address2=29851%20Aventura&state=CA&zipCode=92688',
  'headers': {
    'x-amzn-lambda-proxying-cell': '0',
    'content-length': '0',
    'x-amzn-tls-version': 'TLSv1.2',
    'x-forwarded-proto': 'https',
    'postman-token': '0c5e7075-6bbc-45d3-9cdf-0e1e9b6a5e66',
    'x-forwarded-port': '443',
    'x-forwarded-for': '49.207.203.21',
    'x-amzn-lambda-proxy-auth': 'HmacSHA256, SignedHeaders=x-amzn-lambda-forwarded-client-ip;x-amzn-lambda-forwarded-host;x-amzn-lambda-proxying-cell, Signature=JuBDqQV+A/xnpTXoLfpTawuDozJFyhVqIybiaklZzNI=',
    'accept': '*/*',
    'x-amzn-lambda-forwarded-client-ip': '49.207.203.21',
    'x-amzn-tls-cipher-suite': 'ECDHE-RSA-AES128-GCM-SHA256',
    'x-amzn-trace-id': 'Self=1-656ebf7d-40191c256a6e5a296013f0f9;Root=1-656ebf7d-2548f737627732b73294994e',
    'host': 'iucdfkcxtzbulo7x7vyc7emzh40hngch.cell-1-lambda-url.us-east-1.on.aws',
    'x-amzn-lambda-forwarded-host': 'iucdfkcxtzbulo7x7vyc7emzh40hngch.lambda-url.us-east-1.on.aws',
    'accept-encoding': 'gzip, deflate, br',
    'user-agent': 'PostmanRuntime/7.35.0'
  },
  'queryStringParameters': {
    'zipCode': '92688',
    'address2': '29851 Aventura',
    'address1': 'SUITE K',
    'state': 'CA',
    'city':'California'
  },
  'requestContext': {
    'accountId': 'anonymous',
    'apiId': 'iucdfkcxtzbulo7x7vyc7emzh40hngch',
    'domainName': 'iucdfkcxtzbulo7x7vyc7emzh40hngch.cell-1-lambda-url.us-east-1.on.aws',
    'domainPrefix': 'iucdfkcxtzbulo7x7vyc7emzh40hngch',
    'http': {
      'method': 'GET',
      'path': '/address',
      'protocol': 'HTTP/1.1',
      'sourceIp': '49.207.203.21',
      'userAgent': 'PostmanRuntime/7.35.0'
    },
    'requestId': 'c6fc92df-4dcf-4a25-89b4-5123f6fb5122',
    'routeKey': '$default',
    'stage': '$default',
    'time': '05/Dec/2023:06:13:17 +0000',
    'timeEpoch': 1701756797757
  },
  'isBase64Encoded': False
}




        #mock_response = mock_request.return_value
        mock_response = Mock()
        mock_call_api.return_value = (
    '''
    <?xml version="1.0" ?>
    <ZipCodeLookupResponse>
        <Address ID="1">
            <Address1>STE K</Address1>
            <Address2>29851 AVENTURA</Address2>
            <City>RCHO STA MARG</City>
            <State>CA</State>
            <Zip5>92688</Zip5>
            <Zip4>2014</Zip4>
        </Address>
    </ZipCodeLookupResponse>
    ''',
    {'Content-Type': 'application/xml'}
)
        print('this is the mock response in test file')
        print(mock_response)

        # Act
        result = lambda_handler(event, None)
        print('result in test file')
        print('result is')
        print(result)

        # Assert
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['body'],'\n    <?xml version="1.0" ?>\n    <ZipCodeLookupResponse>\n        <Address ID="1">\n            <Address1>STE K</Address1>\n            <Address2>29851 AVENTURA</Address2>\n            <City>RCHO STA MARG</City>\n            <State>CA</State>\n            <Zip5>92688</Zip5>\n            <Zip4>2014</Zip4>\n        </Address>\n    </ZipCodeLookupResponse>\n    '),
        self.assertEqual(result['headers']['Content-Type'], 'application/xml')

    # Add more test methods for different scenarios...

if __name__ == '__main__':
    unittest.main()
