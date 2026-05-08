from app import app
with app.test_client() as c:
    response = c.get('/login')
    with open('login_rendered.html', 'w', encoding='utf-8') as f:
        f.write(response.data.decode('utf-8'))
