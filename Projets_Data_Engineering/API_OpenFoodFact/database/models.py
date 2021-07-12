from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Document):
  email = db.EmailField(required=True, unique=True)
  password = db.StringField(required=True, min_length=6)
  firstName = db.StringField()
  lastName = db.StringField()
  recipes = db.ListField(db.IntField())
  dailyGoal = db.IntField()

  def hash_password(self):
   self.password = generate_password_hash(self.password).decode('utf8')
 
  def check_password(self, password):
   return check_password_hash(self.password, password)

class Product(db.Document):
  name = db.StringField(required=True)
  description = db.StringField()
  barCode = db.StringField(unique=True, sparse=True)
  caloriesByPortion = db.FloatField(required=True, min_value=0, default=0)
  caloriesBy100gr = db.IntField(required=True, min_value=0, default=0)

class ProductQuantity(db.EmbeddedDocument):
  productId = db.ReferenceField(Product)
  unit = db.StringField()
  quantity = db.IntField()

class DailyIntake(db.Document):
  userId = db.ReferenceField(User)
  date = db.DateTimeField()
  products = db.ListField(db.EmbeddedDocumentField(ProductQuantity))

  def getSumDailyIntake(self):
    list_dailyintake_portion = [p.quantity*p.productId.caloriesByPortion for p in self.products if p.unit=='portion']
    list_dailyintake_gram = [p.quantity/100*p.productId.caloriesBy100gr for p in self.products if p.unit=='gram']
    return sum(list_dailyintake_portion+list_dailyintake_gram)
