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

orders_json_file = "/data/data.json"

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

api = Api(app, version='1.0', title='Orders API',
          description='REST API for managing orders',
          authorizations=authorizations, security='apikey')

orders_ns = api.namespace('api/v1.0/orders', description='Orders API V1.0')

product_item = api.model('Product', {
    'uuid': fields.String(readOnly=True, description='The unique identifier of a product'),
    'name': fields.String(required=True, description='Product name'),
    'price': fields.Float(required=True, description='Product price'),
})

order_item = api.model('Order', {
    'uuid': fields.String(readOnly=True, description='The unique identifier of an order'),
    'products': fields.List(fields.List(fields.Nested(product_item)))
})

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_db.get(jti)
    if entry is None:
        return True
    return entry == 'true'


@orders_ns.route('/')
class Orders(Resource):
    @api.doc(security=[])
    def get(self):
        pass

    @api.response(201, 'Order successfully created.')
    @api.expect(product_item)
    @jwt_required
    def post(self):
        """Creates a new order."""
        if utils.is_file(orders_json_file):
            result = atomic.set_item(str(orders_json_file), request.json)
            if result:
                return {"message": "Order successfully created."}, 201


@orders_ns.route('/<uuid:uuid>')
@api.response(404, 'Order not found.')
class Orders(Resource):
    @api.doc(security=[])
    def get(self, uuid):
        if utils.is_file(orders_json_file):
            results = atomic.get_item(str(orders_json_file), str(uuid))
            if results:
                return results, 200
        return {"message": "Order not found."}, 404

    def put(self, uuid):
        if utils.is_file(orders_json_file):
            results = atomic.update_item(str(orders_json_file), request.json, str(uuid))
            if results:
                return results, 200
        return {"message": "Order not found."}, 404

    def delete(self, uuid):
        pass


# if __name__ == '__main__':
#     app.run(debug=True)
