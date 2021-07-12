#!/usr/bin/env python
# coding: utf-8

# In[30]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyspark
from pyspark.sql import SparkSession
from statistics import mean
from difflib import SequenceMatcher


# In[31]:


# create SparkSession
spark = SparkSession.builder.master("local[*]")                     .appName('SparkSNCF')                     .getOrCreate()

# extract SparkContext
sc = spark.sparkContext


# In[32]:


df = spark.read.csv("C:/Users/cabid/Documents/1ERE_ANNEE/ARCHITECTURE_BIG_DATA/BIG_DATA_ARCHITECTURE/Projet/data_tarifs.csv", sep=";", encoding="utf-8", header=True)


# In[33]:


df = df.drop("Prix d'appel 2nde", "Plein Tarif Loisir 2nde", "Commentaires")
df.show()


# In[34]:


#!pip install geopandas
#!pip install geopy


# In[35]:


from geopy.geocoders import Nominatim
locator = Nominatim(user_agent="myGeocoder")


# In[43]:


rows = df.select('OD').collect()

for i in rows:
    i = str(i)
    i = i.split("-")


# In[29]:


origine_location = locator.geocode("PARIS GARE DE LYON")
print("Latitude = {}, Longitude = {}".format(origine_location.latitude, origine_location.longitude))
#location = locator.geocode(“Champ de Mars, Paris, France”)
#print(“Latitude = {}, Longitude = {}”.format(location.latitude, location.longitude))
#coordonnées gps google maps => 48.8443038,2.3721886


# In[45]:


# Récupérer la latitude + longitude de 'origine' et 'dedstination'
# Calculer la distance avec 'geopy.distance' et 'geodesic'
# Mettre dans de nouvelles colonnes 
# Faire un sort descendant

