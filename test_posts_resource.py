from requests import get, post, delete

# Тестирование апи постов
print(get('http://localhost:8080/api/posts').json())
print(get('http://localhost:8080/api/posts/2').json())
print(post('http://localhost:8080/api/posts', json={'user_id': '3',
                                                    'description': "Пост, сделанный через API",
                                                    'password': "yandex_lyceum", "themes": "1"}).json())
print(delete('http://localhost:8080/api/posts/5/yandex_lyceum').json())
