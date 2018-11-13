import os
from datetime import timedelta
from flask import Flask, request
from flask_restplus import Resource, Api, fields
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, get_jti,
    jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt
)
import redis


redis_db = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
# Enable blacklisting and specify what kind of tokens to check
# against the blacklist
app.config['JWT_SECRET_KEY'] = os.environ['SECRET_KEY']

# Setup the flask-jwt-extended extension. See:
ACCESS_EXPIRES = timedelta(minutes=int(os.environ['ACCESS_EXPIRES']))
REFRESH_EXPIRES = timedelta(days=int(os.environ['REFRESH_EXPIRES']))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = REFRESH_EXPIRES
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(app, version='1.0', title='Products API',
          description='REST API for managing products',
          authorizations=authorizations, security='apikey')

users_ns = api.namespace('auth', description='Users API')

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_db.get(jti)
    if entry is None:
        return True
    return entry == 'true'


# Standard login endpoint
@users_ns.route('/login')
class Login(Resource):
    def post(self):
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        check_login = redis_db.hget("UserAuth", str(username))
        if check_login:
            if check_login == str(password):
                # valid auth
                # Create our JWTs
                access_token = create_access_token(identity=username)
                refresh_token = create_refresh_token(identity=username)

                # Store the tokens in redis with a status of not currently revoked. We
                # can use the `get_jti()` method to get the unique identifier string for
                # each token. We can also set an expires time on these tokens in redis,
                # so they will get automatically removed after they expire. We will set
                # everything to be automatically removed shortly after the token expires
                access_jti = get_jti(encoded_token=access_token)
                refresh_jti = get_jti(encoded_token=refresh_token)
                redis_db.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
                redis_db.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

                ret = {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
                return ret, 200
        return {"msg": "Wrong username and/or password"}, 401


# Standard refresh endpoint. A blacklisted refresh token
# will not be able to access this endpoint
@users_ns.route('/refresh')
class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        # Do the same thing that we did in the login endpoint here
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        access_jti = get_jti(encoded_token=access_token)
        redis_db.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
        ret = {'access_token': access_token}
        return ret, 200


# Endpoint for revoking the current users access token
@users_ns.route('/access_revoke')
class Logout(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        redis_db.set(jti, 'true', ACCESS_EXPIRES * 1.2)
        return {"msg": "Access token revoked"}, 200


# Endpoint for revoking the current users refresh token
@users_ns.route('/refresh_revoke')
class Logout2(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        redis_db.set(jti, 'true', REFRESH_EXPIRES * 1.2)
        return {"msg": "Refresh token revoked"}, 200


# if __name__ == '__main__':
#     app.run(debug=True)
