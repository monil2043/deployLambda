import requests
import xml.etree.ElementTree as ET
from aws_lambda_powertools import Logger, Metrics, Tracer
import os
from utils import log_specific_value,create_correlation_id,log_request_received,log_response_received,handle_bad_request,handle_forbidden,handle_internal_server_error,handle_not_acceptable,handle_not_found,handle_success,handle_unauthorized,parse_and_print_json,parse_and_print_xml,call_api
USER_ID = '7NEURA45X5797'
#os.environ.get('USER_ID')


tracer = Tracer()
logger = Logger()
metrics = Metrics()



@tracer.capture_method
def generate_api_request_params_address_validate(request_query_params):
    xml_str = f'''
        <AddressValidateRequest USERID="{USER_ID}">
            <Revision>1</Revision>
            <Address ID="0">
                <Address1>{request_query_params['address1']}</Address1>
                <Address2>{request_query_params['address2']}</Address2>
                <City/>
                <State>{request_query_params['state']}</State>
                <Zip5>{request_query_params['zipCode']}</Zip5>
                <Zip4/>
            </Address>
        </AddressValidateRequest>
    '''

    return {
        'url': 'https://secure.shippingapis.com/ShippingAPI.dll',
        'method': 'GET',
        'params': {
            'API': 'Verify',
            'XML': xml_str
        }
    }

@tracer.capture_method
def generate_api_request_params_randomAPICall(request_query_params):
    zipCode = request_query_params['zipCode']
    return {
        'url': 'https://api.zippopotam.us/us/' + zipCode,
        'method': 'GET',
        'params': None
    }

@tracer.capture_method
def generate_api_request_params_zipCode_validate(request_query_params):
    xml_str = f'''
        <ZipCodeLookupRequest USERID="{USER_ID}">
            <Address ID="1">
                <Address1>{request_query_params['address1']}</Address1>
                <Address2>{request_query_params['address2']}</Address2>
                <City>{request_query_params['city']}</City>
                <State>{request_query_params['state']}</State>
                <Zip5>{request_query_params['zipCode']}</Zip5>
                <Zip4></Zip4>
            </Address>
        </ZipCodeLookupRequest>
    '''

    return {
        'url': 'https://secure.shippingapis.com/ShippingAPI.dll',
        'method': 'GET',
        'params': {
            'API': 'ZipCodeLookup',
            'XML': xml_str
        }
    }

#url = http://localhost:2772/applications/FeatureFlagImplementation/environments/dev/configurations/featureFlagStore
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    
    log_request_received(event)
    statusCodeValue,body,headerValue =  (call_api("https://f1gb42bn54.execute-api.us-east-1.amazonaws.com/DEV/GetCustomerProfile?keyType=phoneNumber&keyValue=1234","GET"))
    
    return {
        'statusCode': statusCodeValue,
        'body': body,
        'headers': headerValue
        
    }




event = {
  "version": "2.0",
  "routeKey": "$default",
  "rawPath": "/address",
  "rawQueryString": "address1=SUITE%20K&address2=29851%20Aventura&state=CA&zipCode=92688",
  "headers": {
    "x-amzn-lambda-proxying-cell": "0",
    "content-length": "0",
    "x-amzn-tls-version": "TLSv1.2",
    "x-forwarded-proto": "https",
    "postman-token": "0c5e7075-6bbc-45d3-9cdf-0e1e9b6a5e66",
    "x-forwarded-port": "443",
    "x-forwarded-for": "49.207.203.21",
    "x-amzn-lambda-proxy-auth": "HmacSHA256, SignedHeaders=x-amzn-lambda-forwarded-client-ip;x-amzn-lambda-forwarded-host;x-amzn-lambda-proxying-cell, Signature=JuBDqQV+A/xnpTXoLfpTawuDozJFyhVqIybiaklZzNI=",
    "accept": "*/*",
    "x-amzn-lambda-forwarded-client-ip": "49.207.203.21",
    "x-amzn-tls-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
    "x-amzn-trace-id": "Self=1-656ebf7d-40191c256a6e5a296013f0f9;Root=1-656ebf7d-2548f737627732b73294994e",
    "host": "iucdfkcxtzbulo7x7vyc7emzh40hngch.cell-1-lambda-url.us-east-1.on.aws",
    "x-amzn-lambda-forwarded-host": "iucdfkcxtzbulo7x7vyc7emzh40hngch.lambda-url.us-east-1.on.aws",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "PostmanRuntime/7.35.0"
  },
  "queryStringParameters": {
    "zipCode": "92688",
    "address2": "29851 Aventura",
    "address1": "SUITE K",
    "state": "CA"
  },
  "requestContext": {
    "accountId": "anonymous",
    "apiId": "iucdfkcxtzbulo7x7vyc7emzh40hngch",
    "domainName": "iucdfkcxtzbulo7x7vyc7emzh40hngch.cell-1-lambda-url.us-east-1.on.aws",
    "domainPrefix": "iucdfkcxtzbulo7x7vyc7emzh40hngch",
    "http": {
      "method": "GET",
      "path": "/address",
      "protocol": "HTTP/1.1",
      "sourceIp": "49.207.203.21",
      "userAgent": "PostmanRuntime/7.35.0"
    },
    "requestId": "c6fc92df-4dcf-4a25-89b4-5123f6fb5122",
    "routeKey": "$default",
    "stage": "$default",
    "time": "05/Dec/2023:06:13:17 +0000",
    "timeEpoch": 1701756797757
  },
  "isBase64Encoded": False
}

if __name__ == '__main__':
    (lambda_handler(event, None))