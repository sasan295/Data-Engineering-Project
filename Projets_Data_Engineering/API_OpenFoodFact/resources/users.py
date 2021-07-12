from flask import jsonify
from flask import request
from flask import abort
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database.models import User, Product, ProductQuantity, DailyIntake
from .products import getProductByCode

## /users routes
class UsersApi(Resource):
    def get(self):
        users = User.objects()
        return jsonify(users)

    def delete(self):
        users = User.objects().delete()
        return jsonify({message: "all users deleted" % userId})

## /users/<userId> routes
class UserApi(Resource):
    def get(self, userId):
        try:
            user = User.objects.get(id=userId)
            return jsonify(user)
        except Exception as e:
            print(e)
            return {'error': 'User not found : %s' % e}, 404
    
    def put(self, userId):
        body = request.json
        try:
            User.objects.get(id=userId).update(**body)
            return jsonify(User.objects.get(id=userId))
        except Exception as e:
            print(e)
            return {'error': 'User update failed : %s' % e}, 400  

    def delete(self, userId):
        try:
            User.objects.get(id=userId).delete()
            return jsonify({message: "user %s deleted" % userId})
        except Exception as e:
            print(e)
            return {'error': 'Couldnt delete user : %s' % e}, 400

## /users/me
class UserMeApi(Resource):
    @jwt_required()
    def get(self):
        try:
            # extract info from the jwt token
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            return jsonify(user)
        except Exception as e:
            print(e)
            return {'error': 'Internal error : %s' % e}, 500     

## /users/me/goal
class UserMeGoalApi(Resource):
    @jwt_required()
    def put(self):
        body = request.json
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            user.dailyGoal = body["goal"]
            user.save()
            return jsonify(user)
        except Exception as e:
            print(e)
            return {'error': 'Internal error : %s' % e}, 500

## /users/recipes
class UserRecipesApi(Resource):
    @jwt_required()
    def put(self):
        body = request.json
        try:
            # extract info from the jwt token
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            for r in body["recipes"]:
                ## appeller strapi pour récupérer la recette
                if r not in user.recipes:
                    user.recipes.append(r)
            user.save()
            return jsonify(user)
        except Exception as e:
            print(e)
            return {'error': 'Internal error : %s' % e}, 500

## /users/manual/product
class UserManualProductApi(Resource):
    @jwt_required()
    def put(self):
        body = request.json
        product = Product()
        productQuantity = ProductQuantity()
        try:
            product.name = body['name']
            product.description = body['description']
            product.caloriesByPortion = body['caloriesByPortion']
            product.caloriesBy100gr = body['caloriesBy100gr']
            product.save()

            productQuantity.productId = product
            productQuantity.unit = body['unit']
            productQuantity.quantity = body['amount']
        except Exception as e:
            print(e)
            return {'error': 'Internal error : %s' % e}, 500
        if body.get('date') != None:
            return jsonify(createDailyIntake(productQuantity, datetime.strptime(body.get('date'), '%Y-%m-%d').date()))
        else:
            return jsonify(createDailyIntake(productQuantity))

## /users/product/:bar_code
class UserCodeProductApi(Resource):
    @jwt_required()
    def put(self, bar_code):
        body = request.json
        result = None
        productQuantity = ProductQuantity()
        try:
            result = getProductByCode(bar_code)
            product = Product(**result)
            product.save()

            productQuantity.productId = product
            productQuantity.unit = body['unit']
            productQuantity.quantity = body['amount']
        except AttributeError as err:
            return {'error': 'Product not found.'}, 404
        except Exception as e:
            return {'error': 'Internal error : %s' % e}, 500
        if body.get('date') != None:
            return jsonify(createDailyIntake(productQuantity, datetime.strptime(body.get('date'), '%Y-%m-%d').date()))
        else:
            return jsonify(createDailyIntake(productQuantity))

## /users/me/stats/:date
class UserMeStatsApi(Resource):
    @jwt_required()
    def get(self, date):
        sum_dailyIntake = 0
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            date_data = datetime.strptime(date, '%Y-%m-%d').date()
            if DailyIntake.objects.filter(userId=user, date=date_data):
                dailyIntake = DailyIntake.objects.get(userId=user, date=date_data)
                sum_dailyIntake = dailyIntake.getSumDailyIntake()
        except Exception as err:
            print(err)
            return {'error': 'Internal error : %s' % err}, 500
        return {
            "daily_goal" : user.dailyGoal,
            "daily_intake" : sum_dailyIntake,
            "daily_result" : sum_dailyIntake - user.dailyGoal
        }

def createDailyIntake(productQuantity, date=datetime.now().date()):
    try:
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        if DailyIntake.objects.filter(userId=user, date=date):
            dailyIntake = DailyIntake.objects.get(userId=user, date=date)
            dailyIntake.products.append(productQuantity)
        else:
            dailyIntake = DailyIntake()
            dailyIntake.userId = user
            dailyIntake.date = date
            dailyIntake.products.append(productQuantity)
        dailyIntake.save()
    except Exception as err:
        print(err)
        return {'error': 'Internal error : %s' % err}, 500
    return dailyIntake
