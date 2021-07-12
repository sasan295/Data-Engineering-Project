from flask import jsonify
from flask import request
from flask import abort
from flask_restful import Resource
from services.strapi import strapi
import requests
from flask import current_app
from flask import json, Response
from database.models import Product

## /products
class ProductsAPI(Resource):
    def get(self):
        products = Product.objects()
        return jsonify(products)

## /products/<barre_code>
class ProductAPI(Resource):
    def get(self, barre_code):
        result = None
        try:
            # response = Response(getProductByCode(barre_code),content_type="application/json; charset=utf-8" )
            result = getProductByCode(barre_code)
            product = Product(**result)
            product.save()
            return jsonify(product)
            # return jsonify(json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False))
        except AttributeError as err:
            return {'error': 'Product not found.'}, 404
        except Exception as e:
            return {'error': 'Couldnt create product because : %s' % e}, 500

def getProductByCode(barre_code):
    response = requests.get(f'{current_app.config["OPENFOODFACT_URL"]}/api/v0/product/{barre_code}.json')
    product = response.json()
    return {
        "name" : product.get('product').get('product_name'),
        "description" : product.get('product').get('generic_name_fr'),
        "barCode": product.get('code'),
        "caloriesByPortion" : float(product.get('product').get('nutriments').get('energy-kcal_serving')) if product.get('product').get('nutriments').get('energy-kcal_serving') else None,
        "caloriesBy100gr" : int(product.get('product').get('nutriments').get('energy-kcal_100g')) if product.get('product').get('nutriments').get('energy-kcal_100g') else None
    }