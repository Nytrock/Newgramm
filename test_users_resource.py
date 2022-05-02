from requests import get, post, delete

# Тестирование апи пользователей
print(get('http://localhost:8080/api/users').json())
print(get('http://localhost:8080/api/users/1').json())
print(get('http://localhost:8080/api/users/2').json())
print(post('http://localhost:8080/api/users').json())
print(post('http://localhost:8080/api/users', json={'name': 'DTEAA',
                                                    'description': "Один из создателей этого всего",
                                                    'age': 17, "email": "ya_hz@mail.ru",
                                                    'password': "yandex_lyceum", "themes": "1"}).json())
print(delete('http://localhost:8080/api/users/3/yandex_lyceu').json())
