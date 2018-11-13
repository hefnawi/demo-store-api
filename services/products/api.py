import os
from datetime import timedelta
from flask import Flask, request
from flask_restplus import Resource, Api, fields
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, get_jti,
    jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt
)
from json_storage_manager import atomic, utils
import redis


redis_db = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

products_json_file = "/data/data.json"

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

products_ns = api.namespace('api/v1.0/products', description='Products API V1.0')

product_item = api.model('Product', {
    'uuid': fields.String(readOnly=True, description='The unique identifier of a product'),
    'name': fields.String(required=True, description='Product name'),
    'price': fields.Float(required=True, description='Product price'),
})

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_db.get(jti)
    if entry is None:
        return True
    return entry == 'true'


@products_ns.route('/')
class Products(Resource):
    @api.doc(security=[])
    def get(self):
        pass

    @api.response(201, 'Product successfully created.')
    @api.expect(product_item)
    @jwt_required
    def post(self):
        """Creates a new product."""
        if utils.is_file(products_json_file):
            result = atomic.set_item(str(products_json_file), request.json)
            if result:
                return {"message": "Product successfully created."}, 201


@products_ns.route('/<uuid:uuid>')
@api.response(404, 'Product not found.')
class Products(Resource):
    @api.doc(security=[])
    def get(self, uuid):
        if utils.is_file(products_json_file):
            results = atomic.get_item(str(products_json_file), str(uuid))
            if results:
                return results, 200
        return {"message": "Product not found."}, 404

    def put(self, uuid):
        if utils.is_file(products_json_file):
            results = atomic.update_item(str(products_json_file), request.json, str(uuid))
            if results:
                return results, 200
        return {"message": "Product not found."}, 404

    def delete(self, uuid):
        pass


# if __name__ == '__main__':
#     app.run(debug=True)
