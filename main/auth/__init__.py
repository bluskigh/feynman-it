from jose import jwt 
import http.client
from os import environ
from base64 import b64decode
from json import loads


DOMAIN = environ.get('DOMAIN')
AUDIENCE = environ.get('AUDIENCE') 


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
    if len(authorization) != 2 or authorization[0].lower() != 'bearer' or len(authorization[1].split('.')) != 3:
        raise CustomException('Invalid authorization header given')
    return authorization[1]


def filter_jwks(keys):
    return [key for key in keys if 'kid' in key and key.get('kty') == 'RSA' and key.get('use') == 'sig']


def verify_jwt(token):
    jwks = http.client.HTTPSConnection(DOMAIN)
    jwks.request('GET', '/.well-known/jwks.json')
    jwks = jwks.getresponse()
    jwks = loads(jwks.read().decode()).get('keys')
    jwks = filter_jwks(jwks)

    # decoding the header, converting to string by decoding, and loading using json
    header = loads(b64decode(token.split('.')[0]).decode())
    kid = header.get('kid')

    jwk = list(filter(lambda key: key.get('kid') == kid, jwks))

    if len(jwk) == 0:
        print('Could not find exact key')
        return None

    jwk = jwk[0] 
    try:
        return jwt.decode(token=token, audience=AUDIENCE, key=jwk, algorithms=['RS256'], issuer=f'https://{DOMAIN}/')
    except Exception as e:
        raise CustomException(e)
