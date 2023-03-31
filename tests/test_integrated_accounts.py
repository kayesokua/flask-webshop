from flask_login import current_user

def test_accounts_register_as_buyer(client):
    """
    Register as a buyer profile and login.
    """
    client.post('/accounts/register',
        data={
            'username': 'new_buyer',
            'password': 'testpassword',
            'password2': 'testpassword',
            'is_active': True,
            'is_admin': False,
            'accept_tos':  True,}
        )
    client.post('/accounts/login',
        data={
        'username': 'new_buyer',
        'password': 'testpassword'
        })
    response = client.get('/')
    assert response.status_code == 200
    assert "New_buyer" in response.get_data(as_text=True)
    assert "Add Product" not in response.get_data(as_text=True)

def test_accounts_register_as_seller(client):
    """
    Register as a seller profile is not possible in website client.
    Automatically registers as a buyer/browser profile.
    """
    client.post('/accounts/register',
        data={
            'username': 'new_seller',
            'password': 'testpassword',
            'password2': 'testpassword',
            'is_active': True,
            'is_admin': True,
            'accept_tos':  True}
        )
    client.post('/accounts/login',
        data={
        'username': 'new_seller',
        'password': 'testpassword'
        })

    response = client.get('/')
    assert response.status_code == 200
    assert "New_seller" in response.get_data(as_text=True)
    assert "Add Product" not in response.get_data(as_text=True)

