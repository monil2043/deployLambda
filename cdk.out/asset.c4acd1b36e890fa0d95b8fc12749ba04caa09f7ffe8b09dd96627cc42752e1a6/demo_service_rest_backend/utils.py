from aws_lambda_powertools import Logger

logger = Logger()

def log_request_received(event):
    logger.info("Request received", extra={"event": event})

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
