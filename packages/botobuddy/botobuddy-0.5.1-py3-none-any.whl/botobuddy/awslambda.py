
import json
from decimal import Decimal


class DynamoFriendlyEncoder(json.JSONEncoder):
    """
    A JSON encoder that converts Decimal objects to integers.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def response(data_or_error=None, rc=200):
    """
    Returns a response object for the current request.
    Parameters:
    - data_or_error: The data to return in the response.
    - rc: The status code to return in the response.
    Returns:
    - A response object with the following properties:
    - statusCode: The status code to return in the response.
    - headers: The headers to return in the response.
    - body: The body to return in the response.
    """
    if rc != 200:
        payload = {
            'IsSuccessful': False,
            'Error': data_or_error
        }
    else:
        payload = {'IsSuccessful': True}

        if data_or_error:
            payload.update(data_or_error)

    return {
        'statusCode': rc,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT,DELETE'
        },
        'body': json.dumps(payload, cls=DynamoFriendlyEncoder)
    }


def request_params(event):
    """
    Returns the method and parameters of the current request.
    Example: ('GET', {'path': 'example'})
    Example: ('POST', {'body': {'key': 'value'}})
    Example: ('PUT', {'body': {'key': 'value'}})
    Example: ('DELETE', {'path': 'example'})
    Example: ('OPTIONS', {})
    Example: ('PATCH', {'body': {'key': 'value'}})
    Example: ('HEAD', {})
    Example: ('TRACE', {})
    """
    params = dict()
    method = event['httpMethod']

    pathParams = event.get('pathParameters')
    if pathParams:
        params.update(pathParams)

    qsParams = event.get('queryStringParameters')
    if qsParams:
        params.update(qsParams)

    if method == 'POST' or method == 'PUT':
        if 'body' not in event:
            raise UserWarning(
                'A request body must be present for POST and PUT requests'
            )

        params.update(json.loads(event['body']))

    return (method, params)


def get_this_url(event):
    """
    Returns the full URL of the current request.
    Example: https://example.com/path
    """
    requestContext = event['requestContext']
    domainName = requestContext['domainName']
    path = requestContext['path']
    return f'https://{domainName}{path}'
