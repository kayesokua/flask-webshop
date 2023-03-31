from flask_login import login_user
from application.extensions.db import db
from application.models import Product

def test_cart_add_item(client_buyer):
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        response = client.get('/cart/add/2')
        assert response.status_code == 302
        with client.session_transaction() as session:
            assert session['cart'] == [{'id': 2, 'quantity': 1}]

def test_cart_remove_item(client_buyer):
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        client.get('/cart/add/1')
        client.get('/cart/add/2')
        client.get('/cart/add/3')
        response = client.get('/cart/delete/0')
        assert response.status_code == 302
        with client.session_transaction() as session:
            assert session['cart'] == [{'id': 2, 'quantity': 1},{'id': 3, 'quantity': 1}]

def test_handle_cart_free_shipping(client_buyer):
    """
    Test cart function with free shipping
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()

        db.session.add(mock_seller)
        db.session.commit()

        mock_product1 = Product(admin_id=mock_seller.id, name='Mock Product 1', price=9.99, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        mock_product2 = Product(admin_id=mock_seller.id, name='Mock Product 2', price=19.99, stock=20, description='This is a second mock product.', image='https://example.com/image2.png',)
        db.session.add(mock_product2)
        db.session.commit()

        mock_product3 = Product(admin_id=mock_seller.id, name='Mock Product 3', price=29.99, stock=10, description='This is a third mock product.', image='https://example.com/image3.png',)
        db.session.add(mock_product3)
        db.session.commit()

        login_user(mock_buyer)

        client.get('/cart/add/1')
        client.get('/cart/add/2')
        client.get('/cart/add/3')

        response = client.get('/cart')

        gross_total = str(mock_product3.price + mock_product2.price + mock_product1.price)
        payment_with_shipping_fee = str(mock_product3.price + mock_product2.price + mock_product1.price)

        assert response.status_code == 200
        assert gross_total in response.get_data(as_text=True)
        assert payment_with_shipping_fee in response.get_data(as_text=True)
        assert "standard shipping fee of € 0" in response.get_data(as_text=True)

def test_handle_cart_with_shipping_fee(client_buyer):
    """
    Test cart function with shipping fee
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()

        db.session.add(mock_seller)
        db.session.commit()

        mock_product1 = Product(admin_id=mock_seller.id, name='Mock Product 1', price=1.00, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        mock_product2 = Product(admin_id=mock_seller.id, name='Mock Product 2', price=2.00, stock=20, description='This is a second mock product.', image='https://example.com/image2.png',)
        db.session.add(mock_product2)
        db.session.commit()

        mock_product3 = Product(admin_id=mock_seller.id, name='Mock Product 3', price=3.00, stock=10, description='This is a third mock product.', image='https://example.com/image3.png',)
        db.session.add(mock_product3)
        db.session.commit()

        login_user(mock_buyer)

        client.get('/cart/add/1')
        client.get('/cart/add/2')
        client.get('/cart/add/3')

        response = client.get('/cart')

        gross_total = str(mock_product3.price + mock_product2.price + mock_product1.price)
        grand_total = str(mock_product3.price + mock_product2.price + mock_product1.price + 5.99)

        assert response.status_code == 200
        assert gross_total in response.get_data(as_text=True)
        assert grand_total in response.get_data(as_text=True)
        assert "standard shipping fee of € 0" not in response.get_data(as_text=True)
        assert "standard shipping fee of € 5.99" in response.get_data(as_text=True)