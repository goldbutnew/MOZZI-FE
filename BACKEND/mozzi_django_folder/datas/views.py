from django.shortcuts import render
from .models import Foods,Category,Ingredient
from .serializers import FoodSerializer 
import requests
import json
import random
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
import re
from .models import MongoFood  # MongoDB 모델 임포트
import requests
from django.http import JsonResponse
from django.core import serializers

from .models import MongoFood
# 식재료 뽑기
def get_ingredients(start, last):
    URL = f"http://openapi.foodsafetykorea.go.kr/api/2055492edca74694aa38/COOKRCP01/json/{start}/{last}"
    response = requests.get(URL)
    data = response.json()
    
    for item in data['COOKRCP01']['row']:
        # print(item.get('RCP_NM'))
        ingredients_list = item.get('RCP_PARTS_DTLS').split(',')
        for ingredient in ingredients_list:
            # 정규표현식을 사용하여 숫자와 숫자 뒤에 붙은 문자열을 제거
            ingredient_name = re.sub(r'\d+(\S+)', '', ingredient)
            ingredient_name = ingredient_name.strip()  # 좌우 공백 제거
            # print(ingredient_name)
           
     
            


def migrate_food_recipe_from_mongo_to_mysql(request):
    # MongoDB에서 데이터 가져오기
    mongo_foods = MongoFood.objects.all()

    # MySQL의 id 값을 관리하기 위한 변수
    mysql_id = 1

    # MongoDB에서 가져온 데이터를 MySQL 모델의 food_recipe 필드에 저장
    for mongo_food in mongo_foods:
        # 이미 해당 ID의 레코드가 MySQL에 있는지 확인
        try:
            food = Foods.objects.get(id=mysql_id)
            # 이미 레코드가 존재한다면 해당 필드만 업데이트
            food.food_recipe = str(mongo_food.id)
            food.save()
        except Foods.DoesNotExist:
            # 레코드가 존재하지 않는다면 새로운 레코드 생성
            Foods.objects.create(
                id=mysql_id,
                food_name=mongo_food.food_name,
                food_recipe=str(mongo_food.id),  # MongoDB의 ObjectId를 문자열로 변환하여 저장
                food_views=mongo_food.food_views,  # MongoDB의 해당 필드 값을 그대로 사용
                food_pic=mongo_food.food_pic,
                food_salty_rate=mongo_food.food_salty_rate,
                food_sweet_rate=mongo_food.food_sweet_rate,
                food_bitter_rate=mongo_food.food_bitter_rate,
                food_sour_rate=mongo_food.food_sour_rate,
                food_umami_rate=mongo_food.food_umami_rate,
                food_spicy_rate=mongo_food.food_spicy_rate,
                food_category=mongo_food.food_category,
                food_today_views=mongo_food.food_today_views,
                food_category_count=mongo_food.food_category_count,
            )

        # MySQL의 id 값을 증가시킴
        mysql_id += 1

    return JsonResponse("Migration of food_recipe from MongoDB to MySQL is completed.")

def save_food_recipe_mongo(request):
    start = 1
    last = 1001
    URL = f"http://openapi.foodsafetykorea.go.kr/api/2055492edca74694aa38/COOKRCP01/json/{start}/{last}"
    response = requests.get(URL)
    data = response.json()

    for item in data['COOKRCP01']['row']:
        food_recipe = {}
        for key, value in item.items():
                food_recipe[key] = value  # MANUAL로 시작하는 모든 키의 값을 합침
        
        # MongoDB에 저장
        mongo_food = MongoFood(food_recipe=food_recipe)
        mongo_food.save()

    return JsonResponse({'message':'okay'})


def save_food(request):
    start = 1
    last = 1001
    URL = f"http://openapi.foodsafetykorea.go.kr/api/2055492edca74694aa38/COOKRCP01/json/{start}/{last}"
    response = requests.get(URL)
    data = response.json()

    # MongoDB에서 데이터 가져오기
    mongo_foods = MongoFood.objects.all()

    # MongoDB 객체의 개수
    num_mongo_foods = len(mongo_foods)

    # 데이터 가져오기를 위한 MongoDB 객체의 인덱스
    mongo_index = 0

    for item in data['COOKRCP01']['row']:
        # MongoDB에서 가져올 객체가 더 이상 없을 때 루프를 종료합니다.
        if mongo_index >= num_mongo_foods:
            break
        
        # MongoDB에서 가져오는 코드가 변경되었습니다.
        mongo_food = mongo_foods[mongo_index]
        mongo_index += 1

        # 응답에서 'food_pic' 필드에 대한 값이 없을 경우를 확인합니다.
        food_pic = item.get('ATT_FILE_NO_MK')
        if not food_pic:
            # 'food_pic' 필드가 비어 있는 경우를 처리합니다.
            # 이 부분에 대해 원하는 동작을 수행하거나 오류를 처리할 수 있습니다.
            continue
        print(mongo_food.id)
        save_data = {
            'food_name': item.get('RCP_NM'),
            'food_recipe': str(mongo_food.id),  # MongoDB의 ObjectId를 문자열로 변환하여 저장합니다.
            'food_views': 0,
            'food_pic': food_pic,
            'food_salty_rate': 0,
            'food_sweet_rate': 0,
            'food_bitter_rate': 0,
            'food_sour_rate': 0,
            'food_umami_rate': 0,
            'food_spicy_rate': 0,
            'food_category': item.get('RCP_PAT2'),
            'food_today_views': 0,
            'food_category_count': 0,
        }

        serializer = FoodSerializer(data=save_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
  
    return JsonResponse({'message': 'okay'})

@api_view(['GET'])
def get_random_food(request):
    foods = Foods.objects.all()
    all_food_names = [food.food_name for food in foods]
    all_food_pics = [food.food_pic for food in foods]
    random_food_names = random.sample(all_food_names, 6)
    random_food_pics = random.sample(all_food_pics, 6)

    data = {
        'foods':[{
        'foodName': random_food_names,
        'photo': random_food_pics,
        }
        ]

    }
    # print(data)
    return JsonResponse({'data':data},json_dumps_params={'ensure_ascii': False})


def recipe_detail(request):

    body_unicode = request.body.decode('utf-8')
   
    lines = body_unicode.split("\n")

    food_name = None
    for i in range(len(lines)):
        if lines[i] == '\r':
            food_name = lines[i+1]
            break
    
    # 가져온 값 출력
    print()
    print("Received food name:", food_name.strip(),food_name)
    print()
    try:
      
        foodsss = Foods.objects.all()
      
        food = Foods.objects.get(food_name=food_name.strip())
     
        food_recipe_id = food.food_recipe  # MongoDB의 레시피 ID
    
    except Foods.DoesNotExist:
        return JsonResponse({'message': '음식을 찾을 수 없습니다'})
    # MongoDB에서 레시피 ID에 해당하는 레시피를 검색
    try:
        mongo_food = MongoFood.objects.get(id=food_recipe_id)
        # MongoDB의 레시피 ID 반환
   
        return JsonResponse({'data': {
            # 'id': str(mongo_food.id),
            'RCP_PARTS_DTLS': mongo_food.food_recipe["RCP_PARTS_DTLS"],
            'RCP_PAT2': mongo_food.food_recipe["RCP_PAT2"],
            'RCP_NM': mongo_food.food_recipe["RCP_NM"],
            'ATT_FILE_NO_MK': mongo_food.food_recipe["ATT_FILE_NO_MK"],
            'ATT_FILE_NO_MAIN': mongo_food.food_recipe["ATT_FILE_NO_MAIN"],
            'RCP_NA_TIP': mongo_food.food_recipe["RCP_NA_TIP"],
            'MANUAL_IMG01': mongo_food.food_recipe["MANUAL_IMG01"],
            'MANUAL_IMG02': mongo_food.food_recipe["MANUAL_IMG02"],
            'MANUAL_IMG03': mongo_food.food_recipe["MANUAL_IMG03"],
            'MANUAL_IMG04': mongo_food.food_recipe["MANUAL_IMG04"],
            'MANUAL_IMG05': mongo_food.food_recipe["MANUAL_IMG05"],
            'MANUAL_IMG06': mongo_food.food_recipe["MANUAL_IMG06"],
            'MANUAL_IMG07': mongo_food.food_recipe["MANUAL_IMG07"],
            'MANUAL_IMG08': mongo_food.food_recipe["MANUAL_IMG08"],
            'MANUAL_IMG09': mongo_food.food_recipe["MANUAL_IMG09"],
            'MANUAL_IMG10': mongo_food.food_recipe["MANUAL_IMG10"],
            'MANUAL_IMG11': mongo_food.food_recipe["MANUAL_IMG11"],
            'MANUAL_IMG12': mongo_food.food_recipe["MANUAL_IMG12"],
            'MANUAL_IMG13': mongo_food.food_recipe["MANUAL_IMG13"],
            'MANUAL_IMG14': mongo_food.food_recipe["MANUAL_IMG14"],
            'MANUAL_IMG15': mongo_food.food_recipe["MANUAL_IMG15"],
            'MANUAL_IMG16': mongo_food.food_recipe["MANUAL_IMG16"],
            'MANUAL_IMG17': mongo_food.food_recipe["MANUAL_IMG17"],
            'MANUAL_IMG18': mongo_food.food_recipe["MANUAL_IMG18"],
            'MANUAL_IMG19': mongo_food.food_recipe["MANUAL_IMG19"],
            'MANUAL_IMG20': mongo_food.food_recipe["MANUAL_IMG20"],

            'MANUAL01': mongo_food.food_recipe["MANUAL01"],
            'MANUAL02': mongo_food.food_recipe["MANUAL02"],
            'MANUAL03': mongo_food.food_recipe["MANUAL03"],
            'MANUAL04': mongo_food.food_recipe["MANUAL04"],
            'MANUAL05': mongo_food.food_recipe["MANUAL05"],
            'MANUAL06': mongo_food.food_recipe["MANUAL06"],
            'MANUAL07': mongo_food.food_recipe["MANUAL07"],
            'MANUAL08': mongo_food.food_recipe["MANUAL08"],
            'MANUAL09': mongo_food.food_recipe["MANUAL09"],
            'MANUAL10': mongo_food.food_recipe["MANUAL10"],
            'MANUAL11': mongo_food.food_recipe["MANUAL11"],
            'MANUAL12': mongo_food.food_recipe["MANUAL12"],
            'MANUAL13': mongo_food.food_recipe["MANUAL13"],
            'MANUAL14': mongo_food.food_recipe["MANUAL14"],
            'MANUAL15': mongo_food.food_recipe["MANUAL15"],
            'MANUAL16': mongo_food.food_recipe["MANUAL16"],
            'MANUAL17': mongo_food.food_recipe["MANUAL17"],
            'MANUAL18': mongo_food.food_recipe["MANUAL18"],
            'MANUAL19': mongo_food.food_recipe["MANUAL19"],
            'MANUAL20': mongo_food.food_recipe["MANUAL20"],
        

            
        }})
    except MongoFood.DoesNotExist:
        return JsonResponse({'레시피': '음식을 찾을 수 없습니다'})

def get_recipe_list(request):
    foods = Foods.objects.all()
    data = []
    for food in foods:
        food_data = {
            "foodName": food.food_name,
            "photoUrl": food.food_pic
        }
        data.append(food_data)
    return JsonResponse({'foods': data})

def get_ingredient_list(request):
    ingredients = Ingredient.objects.all()
    ingredient_names = [ingredient.ingredient_name for ingredient in ingredients]
    return JsonResponse({'data': {'ingredients': ingredient_names}},json_dumps_params={'ensure_ascii': False})


def get_ingredient_list_per_category(request):
    body_unicode = request.body.decode('utf-8')
    lines = body_unicode.split("\n")

    categories = None
    for i in range(len(lines)):
        if lines[i] == '\r':
            categories = lines[i+1]
            break
    
    ingredients = Ingredient.objects.all()
    foods = []
    for ingredient in ingredients:
        if str(ingredient.category_id) in categories:
            foods.append(ingredient.ingredient_name)
    
    
        
    return JsonResponse({'data': {"foods" : foods}})
    

def get_highest_viewed_food(request):
    # food_today_views 열에서 가장 높은 값을 가진 행을 가져옵니다.
    highest_viewed_food = Foods.objects.order_by('-food_today_views').first()

    # 결과를 JsonResponse로 반환합니다.
    if highest_viewed_food:
        return JsonResponse({"data": {"foodName": highest_viewed_food.food_name, "photo" : highest_viewed_food.food_pic }} )

import os

# 스크립트 파일의 절대 경로를 가져옴
script_dir = os.path.dirname(os.path.abspath(__file__))

def save_category(request):
    # 파일에서 카테고리를 읽어와서 저장합니다.
    file_path = os.path.join(script_dir, 'categories.txt')
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 줄에서 문자열을 읽어와서 공백을 제거합니다.
            category_name = line.strip()
            
            # 데이터베이스에 이미 존재하는지 확인합니다.
            if not Category.objects.filter(category_name=category_name).exists():
                # 존재하지 않으면 새로운 객체를 생성하여 데이터베이스에 저장합니다.
                Category.objects.create(category_name=category_name)

    return JsonResponse({'message': 'ok'})

def save_ingredient(request):
  
    file_path = os.path.join(script_dir, '1.txt')
  
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 줄에서 문자열을 $를 기준으로 분할합니다.
            if '$' in line:
                _, ingredient_name = line.strip().split('$')
                
                # 데이터베이스에 이미 존재하는지 확인합니다.
                if not Ingredient.objects.filter(ingredient_name=ingredient_name).exists():
                    # 존재하지 않으면 새로운 객체를 생성하여 데이터베이스에 저장합니다.
                    Ingredient.objects.create(ingredient_name=ingredient_name, category_id=1)
            else:
                ingredient_name = line.strip()
                # 데이터베이스에 이미 존재하는지 확인합니다.
                if not Ingredient.objects.filter(ingredient_name=ingredient_name).exists():
                    # 존재하지 않으면 새로운 객체를 생성하여 데이터베이스에 저장합니다.
                    Ingredient.objects.create(ingredient_name=ingredient_name, category_id=1)


    return JsonResponse({'message': 'ok'})





def save_ingredients_category(request):
    # 파일에서 데이터를 읽어옵니다.
    file_path = os.path.join(script_dir, 'category.txt')
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 줄에서 문자열을 읽어와서 ','를 기준으로 분할합니다.
            ingredient_name, category_id_str = line.strip().split(',')

            # 카테고리 ID를 정수형으로 변환합니다.
            category_id = int(category_id_str.replace("'",''))

            # 카테고리를 가져옵니다.
            ingredient = Ingredient.objects.get(ingredient_name = ingredient_name)

            # 재료가 이미 존재하는지 확인합니다.
            ingredient.category_id = category_id
            ingredient.save()
    return JsonResponse({'message':'ok'})

mongo_foods = MongoFood.objects.all()
with open('mongo.txt', 'w', encoding='utf-8') as file:
    for mongo in mongo_foods:
        file.write(mongo.food_recipe['RCP_PARTS_DTLS'] + '\n\n')