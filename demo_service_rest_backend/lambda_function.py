import json
import os
import xml.etree.ElementTree as ET

import requests
from aws_lambda_powertools import Logger, Metrics, Tracer

from commonDependency import (
    call_api,
    create_correlation_id,
    handle_bad_request,
    handle_forbidden,
    handle_internal_server_error,
    handle_not_acceptable,
    handle_not_found,
    handle_success,
    handle_unauthorized,
    log_request_received,
    log_response_received,
    log_specific_value,
    parse_and_print_json,
    parse_and_print_xml,
)


tracer = Tracer()
logger = Logger()
metrics = Metrics()

@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    log_request_received(event)
    methodToCall = event['queryStringParameters']['methodToCall']


    #call feature flag to get down the values noted
    featureFlagResponseJsonContent = (call_api('http://localhost:2772/applications/FeatureFlagImplementation/environments/dev/configurations/featureFlagStore','GET'))[1]
    config_data = json.loads(featureFlagResponseJsonContent)
    performActionImplemented = config_data.get('performActionImplemented').get('enabled')

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
    return {}

if __name__ == '__main__':
    (lambda_handler(event, None))