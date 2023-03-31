from flask_login import current_user, login_user
from application.extensions.db import db
from werkzeug.security import check_password_hash

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

def test_accounts_username_already_exists(client_buyer):
    """
    Test login as a buyer profile.
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        response = client.post('/accounts/register',
                data={
                    'username': 'buyer',
                    'password': 'testpassword',
                    'password2': 'testpassword',
                    'is_active': False,
                    'is_admin': True,
                    'accept_tos':  True}
                )
        assert response.status_code == 200
        assert "Username buyer already exists." in response.get_data(as_text=True)

def test_accounts_login_unregistered_user(client):
    """
    Test login with unregistered user
    """
    with client.application.test_request_context():
        response = client.post('/accounts/login',
                data={
            'username': 'unregister_user',
            'password': 'testpassword'
            })
        assert response.status_code == 302
        with client.session_transaction() as session:
            assert 'Please check your login details and try again.' in session['_flashes'][0][1]

def test_accounts_login_as_buyer(client_buyer):
    """
    Test login as a buyer profile.
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        response = client.get('/')
        assert response.status_code == 200
        assert "Welcome back, Buyer!" in response.get_data(as_text=True)
        assert current_user.id == mock_buyer.id

def test_accounts_login_as_seller(client_seller):
    """
    Test login as a seller profile.
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():
        db.session.add(mock_seller)
        db.session.commit()
        login_user(mock_seller)
        response = client.get('/')
        assert response.status_code == 200
        assert "Welcome back, Seller!" in response.get_data(as_text=True)
        assert current_user.id == mock_seller.id

def test_accounts_login_as_browser(client_browser):
    """
    Test login as a browser profile.
    """
    client, mock_browser = client_browser
    with client.application.test_request_context():
        db.session.add(mock_browser)
        db.session.commit()
        login_user(mock_browser)
        response = client.get('/')
        assert response.status_code == 200
        assert "Welcome back, Browser!" in response.get_data(as_text=True)
        assert current_user.id == mock_browser.id

def test_accounts_login_incorrect_password(client_buyer):
    """
    Test login as a buyer profile.
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        response = client.post('/accounts/login',
                data={
            'username': 'buyer',
            'password': 'WrongPassword!'
            })
        assert response.status_code == 302
        with client.session_transaction() as session:
            assert 'Please check your login details and try again.' in session['_flashes'][0][1]

def test_accounts_logout(client_buyer):
    """
    Test logout as a buyer profile.
    """
    client, mock_buyer, _ = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        response = client.get('/accounts/logout')
        assert response.status_code == 302