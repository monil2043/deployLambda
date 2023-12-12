import requests
import xml.etree.ElementTree as ET
from aws_lambda_powertools import Logger, Metrics, Tracer
import os
import json
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

@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    log_request_received(event)
    methodToCall = event['queryStringParameters']['methodToCall']


    #call feature flag to get down the values noted
    featureFlagResponseJsonContent = (call_api('http://localhost:2772/applications/FeatureFlagImplementation/environments/dev/configurations/featureFlagStore','GET'))[1]
    config_data = json.loads(featureFlagResponseJsonContent)
    performActionImplemented = config_data.get('performActionImplemented').get('enabled')
    getCustomerProfileImplemented = config_data.get('getCustomerProfileImplemented').get('enabled')

    if methodToCall == 'GetCustomerProfile':
        if performActionImplemented:
            statusCodeValue,body,headerValue =  (call_api('https://f1gb42bn54.execute-api.us-east-1.amazonaws.com/DEV/GetCustomerProfile?keyType=phoneNumber&keyValue=1234','GET'))
            return {
            'statusCode': statusCodeValue,
            'body': body,
            'headers': headerValue

            }
        else:
            return handle_not_found('method not found')

    elif methodToCall == 'PerformAction':
        if performActionImplemented:
            statusCodeValue,body,headerValue =  (call_api('https://f1gb42bn54.execute-api.us-east-1.amazonaws.com/DEV/PerformAction','POST'))
            return {
            'statusCode': statusCodeValue,
            'body': body,
            'headers': headerValue

            }
        else:
            return handle_not_found('implementation not found')

    return {}

if __name__ == '__main__':
    (lambda_handler(event, None))
