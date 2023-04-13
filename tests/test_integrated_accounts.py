from flask_login import current_user, login_user
from application.extensions.db import db
from werkzeug.security import check_password_hash
from flask import session
from application.models.accounts import User, DeliveryAddress

def test_accounts_register_as_buyer(client_buyer):
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        client.post('/accounts/register',
            data={
                'username': mock_buyer.username,
                'password': mock_buyer.password,
                'password2': mock_buyer.password,
                'accept_tos': True,
                'is_active': True,
                'is_admin': False
            }
        )
        client.post('/accounts/login',
            data={
            'username': mock_buyer.username,
            'password': mock_buyer.password
            })
        response = client.get('/')
        assert response.status_code == 200
        assert "Buyer" in response.get_data(as_text=True)


def test_accounts_register_as_seller(client_seller):
    """
    Register as a seller profile is not possible in website client.
    Automatically registers as a buyer/browser profile.
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():

        client.post('/accounts/register',
            data={
                'username': mock_seller.username,
                'password': mock_seller.password,
                'password2': mock_seller.password,
                'accept_tos': True,
                'is_active': True,
                'is_admin': True
            }
        )
        client.post('/accounts/login',
            data={
            'username': mock_seller.username,
            'password': mock_seller.password
            })
        response = client.get('/')
        assert response.status_code == 200
        assert "Seller" in response.get_data(as_text=True)
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
                    'username': mock_buyer.username,
                    'password': mock_buyer.password,
                    'password2': mock_buyer.password,
                    'is_active': False,
                    'is_admin': True,
                    'accept_tos':  True}
                )
        assert response.status_code == 200
        assert "Username is already taken" in response.get_data(as_text=True)

def test_accounts_login_unregistered_user(client):
    """
    Test login with unregistered user
    """
    response = client.post('/accounts/login',
                           data={
                    'username': 'DoesNotExist',
                    'password': 'PassWord123!'}
                )
    assert response.status_code == 200
    assert "Invalid username or password" in response.get_data(as_text=True)

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
        assert response.status_code == 200
        assert "Invalid username or password" in response.get_data(as_text=True)

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

def test_add_delivery_address(client_buyer):
    client, mock_buyer, _ = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        client.post('/accounts/addresses/new',
            data={
                'first_name': 'Mei',
                'last_name': 'Xing',
                'email': 'xing.mei@gmail.com',
                'delivery_house_nr': '76',
                'delivery_street': 'Budapester Strasse',
                'delivery_postal': '25579',
                'delivery_state': 'Schleswig-Holstein',
                'delivery_country': 'DE',
                'delivery_additional': 'c/o Ling Ling',
                'instructions': 'Please knock on the door',
            })
        response = client.get('/accounts/addresses/1/update')

        assert response.status_code == 200
        assert "Budapester Strasse" in response.get_data(as_text=True)
        assert "Please knock on the door" in response.get_data(as_text=True)

def test_update_delivery_address(client_buyer):
    client, mock_buyer, _ = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        new_address = DeliveryAddress(
            first_name='Mei',
            last_name='Xing',
            email='xing.mei@gmail.com',
            delivery_house_nr='76',
            delivery_street='Budapester Strasse',
            delivery_postal='25579',
            delivery_state='Schleswig-Holstein',
            delivery_country='DE',
            delivery_additional='c/o Ling Ling',
            instructions='Please knock on the door',
            user_id=mock_buyer.id)
        db.session.add(new_address)
        db.session.commit()
        client.get('/accounts/addresses/1/update')
        client.post('/accounts/addresses/1/update',
            data={
                'first_name': 'Ling',
                'last_name': 'Ling',
                'email': 'ling.ling@gmail.com',
                'delivery_house_nr': '76',
                'delivery_street': 'Budapester Strasse',
                'delivery_postal': '25579',
                'delivery_state': 'Schleswig-Holstein',
                'delivery_country': 'DE',
                'delivery_additional': 'c/o Xing Mei',
                'instructions': 'Please knock on the door',
            })
        response = client.get('/accounts/addresses/1/update')
        assert response.status_code == 200
        assert "ling.ling@gmail.com" in response.get_data(as_text=True)
        assert "c/o Xing Mei" in response.get_data(as_text=True)

def test_delete_delivery_address(client_buyer):
    client, mock_buyer, _ = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        new_address = DeliveryAddress(
            first_name='Mei',
            last_name='Xing',
            email='xing.mei@gmail.com',
            delivery_house_nr='76',
            delivery_street='Budapester Strasse',
            delivery_postal='25579',
            delivery_state='Schleswig-Holstein',
            delivery_country='DE',
            delivery_additional='c/o Ling Ling',
            instructions='Please knock on the door',
            user_id=current_user.id)
        db.session.add(new_address)
        db.session.commit()
        client.get('/accounts/addresses/1/update')
        client.post('/accounts/addresses/delete',
            data={'address_id': 1})
        response = client.get('/accounts/settings')
        assert response.status_code == 200
        assert "No Address" in response.get_data(as_text=True)