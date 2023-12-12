from aws_lambda_powertools import Logger,Tracer
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom

logger = Logger()
tracer = Tracer()


def log_specific_value(name, value):
    logger.info({f'{name}': value})


def create_correlation_id(value):
    logger.info({"correlation_id": value})

def log_request_received(event):
    logger.info("Request received", extra={"event": event})

def log_response_received(event):
    logger.info("Response received", extra={"response": event})

def log_error(exception):
    logger.error("An error occurred", exc_info=exception)

def handle_success(response_body):
    return {
        "statusCode": 200,
        "body": response_body,
    }

def handle_bad_request(error_message):
    return {
        "statusCode": 400,
        "body": error_message,
    }

def handle_unauthorized(error_message):
    return {
        "statusCode": 401,
        "body": error_message,
    }

def handle_forbidden(error_message):
    return {
        "statusCode": 403,
        "body": error_message,
    }

def handle_not_found(error_message):
    return {
        "statusCode": 404,
        "body": error_message,
    }

def handle_not_acceptable(error_message):
    return {
        "statusCode": 406,
        "body": error_message,
    }

def handle_internal_server_error(error_message):
    log_error(error_message)
    return {
        "statusCode": 500,
        "body": "Internal Server Error",
    }

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
def call_api(url, method, params=None):
    try:
        response = requests.request(method, url, params=params)
        content_type = response.headers.get('content-type', '')

        if response.status_code == 200:
            result = handle_success(response.text)
            statusCode, body, headers = 200, result.get("body"),{'Content-Type': 'application/json'}
        elif response.status_code == 400:
            result = handle_bad_request(response.text)
            statusCode , body, headers = 400, result.get("body"),{'Content-Type': 'application/json'}
        elif response.status_code == 401:
            # Handle unauthorized
            result = handle_unauthorized(response.text)
            statusCode , body, headers = 401, result.get("body"),{'Content-Type': 'application/json'}
        elif response.status_code == 403:
            # Handle forbidden
            result = handle_forbidden(response.text)
            statusCode , body, headers = 403, result.get("body"),{'Content-Type': 'application/json'}
        elif response.status_code == 404:
            # Handle not found
            result = handle_not_found(response.text)
            statusCode , body, headers = 404, result.get("body"),{'Content-Type': 'application/json'}
        elif response.status_code == 406:
            # Handle not acceptable
            result = handle_not_acceptable(response.text)
            statusCode , body, headers = 406, result.get("body"),{'Content-Type': 'application/json'}
        else:
            # Handle other status codes as internal server error
            result = handle_internal_server_error(response.text)
            statusCode , body, headers = 500, result.get("body"),{'Content-Type': 'application/json'}

        return statusCode, body, headers

    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")
        # Handle other errors as internal server error
        result = handle_internal_server_error(str(e))
        return result.get("body"), {'Content-Type': 'application/json'}