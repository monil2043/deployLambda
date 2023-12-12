import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
from aws_lambda_powertools import Logger, Metrics, Tracer
#from aws_lambda_powertools.middleware import power_lambda_handler
import os
USER_ID = os.environ.get('USER_ID')


tracer = Tracer()
logger = Logger()
metrics = Metrics()


@tracer.capture_method
def parse_and_print_json(response):
    try:
        json_response = response.json()
        print('Printing JSON response:')
        print(json_response)
        return json_response
    except ValueError:
        print('Error parsing JSON response. Printing raw text:')
        print(response.text)
        return None
@tracer.capture_method
def parse_and_print_xml(response):
    try:
        xml_response = xml.dom.minidom.parseString(response.text)
        pretty_xml = xml_response.toprettyxml()
        print('Pretty Printed XML:')
        print(pretty_xml)
        return pretty_xml
    except Exception as xml_error:
        print('Error parsing XML:', xml_error)
        return None
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

@tracer.capture_method
def call_api(url, method='GET', params=None):
    try:
        response = requests.request(method, url, params=params)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            parsed_response = parse_and_print_json(response)
            return parsed_response, {'Content-Type': 'application/json'}
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            parsed_response = parse_and_print_xml(response)
            return parsed_response, {'Content-Type': 'application/xml'}
        else:
            return response.text, {'Content-Type': content_type}
    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")
        return None, {}
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    print('event is:')
    print(event)
    correlation_id = event['queryStringParameters']['zipCode']
    logger.info({"correlation_id": correlation_id}, "Processing event zipCode")

    request_query_params = event['queryStringParameters']

    print('request_query_params is:')
    print(request_query_params)

    try:
        print('this is the api request params')
        api_request_params = generate_api_request_params_address_validate(request_query_params)
        #api_request_params = generate_api_request_params_zipCode_validate(request_query_params)
        #api_request_params = generate_api_request_params_randomAPICall(request_query_params)
        response, headers = call_api(**api_request_params)
        return {
            'statusCode': 200,
            'body': response,
            'headers': headers
        }
    except Exception as e:
        print('Error:', e)
        return {
            'statusCode': 500,
            'body': 'Error making request'
        }


if __name__ == '__main__':
    print(lambda_handler(event, None))
