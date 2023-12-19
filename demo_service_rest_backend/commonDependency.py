import inspect
import xml.dom.minidom
import xml.etree.ElementTree as ET
from functools import wraps

import requests
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

def dump_args(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        print(f"{func.__module__}.{func.__qualname__} ( {func_args_str} )")
        return func(*args, **kwargs)

    return wrapper


@dump_args
def create_correlation_id(value):
    logger.info({'correlation_id': value})

@dump_args
def log_request_received(event):
    pass

@dump_args
def log_response_received(event):
    logger.info('Response received', extra={'response': event})

@dump_args
def log_error(exception):
    logger.error('An error occurred', exc_info=exception)

@dump_args
def handle_success(response_body):
    return {
        'statusCode': 200,
        'body': response_body,
    }

@dump_args
def handle_bad_request(error_message):
    return {
        'statusCode': 400,
        'body': error_message,
    }

@dump_args
def handle_unauthorized(error_message):
    return {
        'statusCode': 401,
        'body': error_message,
    }

@dump_args
def handle_forbidden(error_message):
    return {
        'statusCode': 403,
        'body': error_message,
    }

@dump_args
def handle_not_found(error_message):
    return {
        'statusCode': 404,
        'body': error_message,
    }

@dump_args
def handle_not_acceptable(error_message):
    return {
        'statusCode': 406,
        'body': error_message,
    }

@dump_args
def handle_internal_server_error(error_message):
    log_error(error_message)
    return {
        'statusCode': 500,
        'body': 'Internal Server Error',
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

@dump_args
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
    
@dump_args
@tracer.capture_method
def call_api(url, method, params=None):
    try:
        response = requests.request(method, url, params=params)
        content_type = response.headers.get('content-type', '')

        # Define a mapping of status codes to handler functions
        status_handlers = {
            200: handle_success,
            400: handle_bad_request,
            401: handle_unauthorized,
            403: handle_forbidden,
            404: handle_not_found,
            406: handle_not_acceptable,
        }

        # Default handler for unknown status codes
        default_handler = handle_internal_server_error

        # Get the appropriate handler based on the status code
        status_code = response.status_code
        handler = status_handlers.get(status_code, default_handler)

        # Call the handler function
        result = handler(response.text)

        # Extract common values
        statusCode, body, headers = status_code, result.get('body'), {'Content-Type': 'application/json'}

        return statusCode, body, headers

    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")
        # Handle other errors as internal server error
        result = handle_internal_server_error(str(e))
        return result.get('body'), {'Content-Type': 'application/json'}
