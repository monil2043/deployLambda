import json
import os
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
    parse_and_print_json,
    parse_and_print_xml,
)

tracer = Tracer()
logger = Logger()
metrics = Metrics()
FEATURE_FLAG_URL = os.environ.get('FEATURE_FLAG_URL')
CUSTOMER_PROFILE_URL = os.environ.get('CUSTOMER_PROFILE_URL')


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    log_request_received(event)

    #call feature flag to get down the values noted
    featureFlagResponseJsonContent = (call_api(FEATURE_FLAG_URL, 'GET'))[1]
    config_data = json.loads(featureFlagResponseJsonContent)
    performActionImplemented = config_data.get('performActionImplemented', {}).get('enabled', True)

    if performActionImplemented:
        statusCodeValue, body, headerValue = (
            call_api(CUSTOMER_PROFILE_URL, 'GET'))
        return {'statusCode': statusCodeValue, 'body': body, 'headers': headerValue}
    else:
        return handle_not_found('method not found')


if __name__ == '__main__':
    (lambda_handler(event, None))
