from flask_restful import reqparse

# Пасер для запросов к постам
parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('description', required=True)
parser.add_argument('themes', required=True)
parser.add_argument('password', required=True)
