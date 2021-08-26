# for getting inputs passed to program
import sys
# for coercing bytestring<->python dict
from json import dumps, loads
# for retrieving/setting environment variables
from os import environ
# for encoding
from base64 import b64decode, b64encode
# for making request
import http.client

from dotenv import find_dotenv
# for encrypting token
from nacl import public, encoding
# for verifying token
from jose import jwt


# GITHUB
ACCESS_TOKEN = sys.argv[1] # token that is found in developer tab
TESTING_TOKEN = sys.argv[2] # current testing token being used by github secrets
# AUTH0
DOMAIN = sys.argv[3] # domain of auth0 
AUDIENCE = sys.argv[4] # audience of auth0
AUDIENCE_TESTING_TOKEN= sys.argv[5]
CLIENT_ID = sys.argv[6] # client id of auth0
CLIENT_SECRET = sys.argv[7] # cilent secret of auth0
GRANT_TYPE = sys.argv[8] # grant-type of auth0
ALGORITHMS = sys.argv[9].split(',') # algoriths accepted by auth0


def set_testing_token():
    """
    Since we want to use TESTING_TOKEN in django tests, we need to have a way to somehow store the token
    in the environment. Therefore will store in .env, use find_dotenv to find file when in tests.py,
    load_dotenv, which will fill environ with new values. Badda bing badda boom, testing token is available 
    """
    env_location = find_dotenv('.testing_token_env')
    if env_location in '':
        env_location = '.testing_token_env'
    with open(env_location, 'w') as f:
        f.write(f'TESTING_TOKEN={environ.get("TESTING_TOKEN")}')


def fetch_new_testing_token():
    """
    Makes a request to auth0 domain for a testing key
    Steps: 
        1. Create pending connection
        2. Create payload as required by auth0  
        3. Make POST request to pending connection with headers indicating dumped payload is of type json
        4. Coerce bytestring response into json, and retrieve new testing token 
        5. Set testing token as environment variable for other methods to use (TODO: decide if to just set a global variable instead, perhaps keeping history of env in bash is no bueno)
    """
    token = http.client.HTTPSConnection(DOMAIN)
    payload = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': GRANT_TYPE, 'audience': AUDIENCE_TESTING_TOKEN}
    token.request('POST', '/oauth/token', dumps(payload), headers={'content-type': 'application/json'})
    token = loads(token.getresponse().read().decode()).get('access_token')
    environ['TESTING_TOKEN'] = token


def save_key():
    """
    Consecutively executes three important steps in order to save a new testing key to github secrets, to be used in future github action workflows.
    Steps:
        - Define a header dict to be used throughout method 
        - Create a pending connection to api.github.com 

        1. Get repo public key to encrypt new token 
            - make a request to: GET '/repos/{owner}/{repo}/actions/secrets/public-key
            - read response, decode back to utf-8, now string, coerce value to dict 
            - retrieve following: key_id, key
        2. Encrypt new token with public key (https://pynacl.readthedocs.io/en/stable/public/#nacl-public-sealedbox)
            - Create instance of PublicKey which corresspond with private key (public_key bytes, encoder that is able to decode the public_key)
            - create instance of a SealedBox using reciever key (public_key recieved from api call in step 2)
            - encrypt using the sealedbox (plaintext), encrypt using base64, then decode to bytestring
        3. Update secret/Create secret with encrypted token
            - make a request to: PUT '/repos/{owner}/{repo}/actions/secrets/{SECRET_NAME}
                - needs body: key_id, encrypted_value
    """

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {ACCESS_TOKEN}',
        'user-agent': 'python'
    }

    conn = http.client.HTTPSConnection('api.github.com')

    """
    >>>> Get public key, and key_id
    """
    conn.request('GET', 
        '/repos/molinitomario/feynman-it/actions/secrets/public-key', 
        headers=headers)
    res = loads(conn.getresponse().read().decode())
    public_key_id = res.get('key_id')
    public_key = res.get('key')

    """
    >>>> Encrypt new token with public key from step above 
    """
    public_key = public.PublicKey(public_key.encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    token_encrypted = b64encode(sealed_box.encrypt(environ.get('TESTING_TOKEN').encode())).decode() 

    """
    >>>> Update secret with encrypted value
    """
    conn.request('PUT', 
        '/repos/molinitomario/feynman-it/actions/secrets/TESTING_TOKEN',
        dumps({'key_id': public_key_id, 
               'encrypted_value': token_encrypted}),
        headers=headers)
    res = conn.getresponse()
    print(res.status)
    # 204 = response when updating a secret 
    # 200 = response when creatina a secret
    if res.status == 200 or res.status == 204:
        print('Successfully set secret with new encrypted value') 
    else:
        # this should stop the test from running and prevent workflow from finishing thus preventing the push to the repo 
        raise Exception('Could not set secret')


def verify_jwt():
    """
    Using the token given to program when running testing_key.py (this program)
    attempt to verify that its a valid token. If not valid, fetch a new testing token, 
    since current testing token is not good anymore, and set the TESTING_TOKEN in github secrets 
    to new encrypted working testing token just fetched from auth0.
    """

    # get jwks that are availbel in the discovery endpoint and or from the .well-known/jwks.json route
    conn = http.client.HTTPSConnection(DOMAIN)
    conn.request('GET', '/.well-known/jwks.json')
    jwks = loads(conn.getresponse().read().decode()).get('keys')

    # get kid from header of token being used
    kid = loads(b64decode(TESTING_TOKEN.split('.')[0]).decode()).get('kid')

    # filter jwks
    jwks = [key for key in jwks if 'kid' in key and key.get('use') == 'sig' and key.get('kty') == 'RSA']

    # get exact jwk
    jwk = list(filter(lambda key: key.get('kid') == kid, jwks))[0]

    print('>>> Below is the testing token')
    print(TESTING_TOKEN)
    try:
        # verify token is valid using specific jwk
        jwt.decode(token=TESTING_TOKEN, key=jwk, audience=AUDIENCE, algorithms=ALGORITHMS, issuer=f'https://{DOMAIN}/')
        # is valid set that token as the testing_token
        environ['TESTING_TOKEN'] = TESTING_TOKEN 
        print('No need to set or create a testing token, current token is valid.') 
    except Exception as e:
        print('Was invalid')
        # not valid get a new key, and set as TESTING_TOKEN in environmental variables
        fetch_new_testing_token()
        # then save the token in repos secrets
        save_key()
    
    set_testing_token()

if __name__ == '__main__':
    verify_jwt()
