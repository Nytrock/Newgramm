from requests import get, post, delete

print(get('http://localhost:8080/api/comments').json())
print(post('http://localhost:8080/api/comments', json={'user_id': '1',
                                                       'post_id': "1",
                                                       'password': "capibara6002",
                                                       "text": "Комментарий, сделанный через API"}).json())
print(get('http://localhost:8080/api/comments/1').json())
print(get('http://localhost:8080/api/comments/2').json())
print(delete('http://localhost:8080/api/comments/2/capibara6002').json())
