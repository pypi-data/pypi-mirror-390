import json

from botobuddy.common import get_secretsmanager_client


def get_sm_secret(name, plain=False, session_config={}):
    sm = get_secretsmanager_client(session_config)
    get_secret_value_response = sm.get_secret_value(SecretId=name)
    secret_string = get_secret_value_response['SecretString']

    if plain:
        return secret_string
    else:
        return json.loads(secret_string)
