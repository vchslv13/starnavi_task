Starnavi test task

Example of API usage:

    >>> import requests as r
    
    # signup new user
    >>> r.post('http://127.0.0.1:8000/api/users/', json={'email': 'test@email.com', 'username': 'test_user', 'password': 'test_passwd', 'full_name': 'Test Name'})
    <Response [201]>
    
    # receive authorization token
    >>> res = r.post('http://127.0.0.1:8000/api/token/', json={'username': 'test_user', 'password': 'test_passwd'})               
    >>> token = res.json()['access']                                       
    >>> h = {'Authorization': f'Bearer {token}'}
    
    # attempt to update user data without authorization
    >>> r.patch('http://127.0.0.1:8000/api/users/8/', json={'email': 'test_new@email.com'})                                                                             
    <Response [401]>
    
    # with authorization
    >>> r.patch('http://127.0.0.1:8000/api/users/8/', json={'email': 'test_new@email.com'}, headers=h)
    <Response [200]>
    >>> r.get('http://127.0.0.1:8000/api/users/8/').json()                                               
    {'url': 'http://127.0.0.1:8000/api/users/8/', 'id': 8, 'username': 'test_user', 'full_name': 'Test Name', 'date_joined': '2019-06-12T04:43:30.221529Z', 'email': 'test_new@email.com'}
    
    # new post
    >>> res = r.post('http://127.0.0.1:8000/api/posts/', json={'text': 'my post'}, headers=h)
    >>> res.json()
    {'url': 'http://127.0.0.1:8000/api/posts/2/', 'id': 2, 'text': 'my post', 'author': 'http://127.0.0.1:8000/api/users/8/', 'creation_datetime': '2019-06-12T04:47:36.676543Z', 'liked_by_users': []}
    
    # like post
    >>> r.post('http://127.0.0.1:8000/api/posts/2/like_post/', headers=h)
    <Response [200]>
    >>> r.get('http://127.0.0.1:8000/api/posts/2/').json()
    {'url': 'http://127.0.0.1:8000/api/posts/2/', 'id': 2, 'text': 'my post', 'author': 'http://127.0.0.1:8000/api/users/8/', 'creation_datetime': '2019-06-12T04:47:36.676543Z', 'liked_by_users': ['http://127.0.0.1:8000/api/users/8/']}
    
    # unlike post
    >>> r.post('http://127.0.0.1:8000/api/posts/2/unlike_post/', headers=h)
    <Response [200]>
    >>> r.get('http://127.0.0.1:8000/api/posts/2/').json()
    {'url': 'http://127.0.0.1:8000/api/posts/2/', 'id': 2, 'text': 'my post', 'author': 'http://127.0.0.1:8000/api/users/8/', 'creation_datetime': '2019-06-12T04:47:36.676543Z', 'liked_by_users': []}



[email_verification](https://github.com/vchslv13/starnavi_task/tree/email_verification) branch contains the rough draft (untested, non-workable) of verifying the users email.
