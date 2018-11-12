from flask import Flask, request
from flask_restplus import Resource, Api, fields
from json_storage_manager import atomic, utils


products_json_file = "data.json"

app = Flask(__name__)

api = Api(app, version='1.0', title='Products API',
          description='REST API for managing products')

products_ns = api.namespace('api/v1.0/products', description='Products API V1.0')


product_item = api.model('Product', {
    'uuid': fields.String(readOnly=True, description='The unique identifier of a product'),
    'name': fields.String(required=True, description='Product name'),
    'price': fields.Float(required=True, description='Product price'),
})

@products_ns.route('/')
class Products(Resource):
    def get(self):
        pass

    @api.response(201, 'Product successfully created.')
    @api.expect(product_item)
    def post(self):
        """Creates a new product."""
        if utils.is_file(products_json_file):
            result = atomic.set_item(str(products_json_file), request.json)
            if result:
                return {"message": "Product successfully created."}, 201


@products_ns.route('/<uuid:uuid>')
@api.response(404, 'Product not found.')
class Products(Resource):
    def get(self, uuid):
        if utils.is_file(products_json_file):
            results = atomic.get_item(str(products_json_file), str(uuid))
            if results:
                return results, 200
        return {"message": "Product not found."}, 404

    def put(self):
        pass

    def delete(self):
        pass


if __name__ == '__main__':
    app.run(debug=True)
