from jose import jwt 
from requests import get
from os import environ
from base64 import b64decode
from json import loads

AUTH_DOMAIN = environ.get('AUTH_DOMAIN')
ALGORITHMS = environ.get('ALGORITHMS')
API_AUDIENCE = environ.get('API_AUDIENCE')
DISCOVERY_ENDPOINT = f'https://{AUTH_DOMAIN}/.well-known/openid-configuration'


class CustomException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def get_token_from_header(request):
    """Gets token from authorization header"""
    if 'Authorization' not in request.headers:
        raise CustomException('Authorization was not in header')
    authorization = request.headers.get('Authorization')
    authorization = authorization.split(' ')
    print(authorization)
    if len(authorization) != 2 or authorization[0].lower() != 'bearer' or len(authorization[1].split('.')) != 3:
        raise CustomException('Invalid authorization header given')
    return authorization[1]


def filter_jwks(keys):
    return [key for key in keys if 'kid' in key and key.get('kty') == 'RSA' and key.get('use') == 'sig']


def verify_jwt(token):
    jwks = get(get(DISCOVERY_ENDPOINT).json().get('jwks_uri')).json()
    jwks = filter_jwks(jwks.get('keys'))
    
    # kid from jwt 
    kid = loads(b64decode(token.split('.')[0]).decode('utf-8')).get('kid')

    # getting exact signature verification key
    jwk = list(filter(lambda key: key.get('kid') == kid, jwks))[0]

    try:
        payload = jwt.decode(token=token, key=jwk, algorithms=ALGORITHMS, audience=API_AUDIENCE, issuer=f'https://{AUTH_DOMAIN}/')
        return payload
    except jwt.ExpiredSignatureError as e:
        raise CustomException(e)
    except jwt.JWTClaimsError as e:
        raise CustomException(e)
    except jwt.JWTClaimsError as e:
        raise CustomException(e)
    except Exception as e:
        raise CustomException(e)
