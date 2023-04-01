from application.extensions.db import db
from flask_login import login_user, current_user
from application.models import Product

def test_index(client):
    """
    Tests that the index page loads correctly.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert "Flask Store" in response.get_data(as_text=True)
    assert "Log In" in response.get_data(as_text=True)

def test_index_by_buyer(client_buyer):
    """
    Tests that the index page loads correctly and that the correct navigation are displayed for a buyer.
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        response = client.get('/')
        assert response.status_code == 200
        assert "Flask Store" in response.get_data(as_text=True)
        assert (mock_buyer.username).capitalize() in response.get_data(as_text=True)
        assert "Add Product" not in response.get_data(as_text=True)

def test_index_by_browser(client_browser):
    """
    Tests that the index page loads correctly and that the correct navigation are displayed for a browser.
    """
    client, mock_browser = client_browser
    with client.application.test_request_context():
        db.session.add(mock_browser)
        db.session.commit()
        login_user(mock_browser)
        response = client.get('/')
        assert response.status_code == 200
        assert "Flask Store" in response.get_data(as_text=True)
        assert (mock_browser.username).capitalize() in response.get_data(as_text=True)
        assert "Add Product" not in response.get_data(as_text=True)

def test_index_by_seller(client_seller):
    """
    Tests that the index page loads correctly and that the correct navigation are displayed for a seller.
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():
        db.session.add(mock_seller)
        db.session.commit()
        login_user(mock_seller)
        response = client.get('/')
        assert response.status_code == 200
        assert "Flask Store" in response.get_data(as_text=True)
        assert (mock_seller.username).capitalize() in response.get_data(as_text=True)
        assert "Add Product" in response.get_data(as_text=True)

def test_read_product_incorrect_id(client_buyer):
    """
    Tests that a product with an incorrect id returns a 404 error.
    """
    client, mock_buyer, mock_seller = client_buyer
    with client.application.test_request_context():
        db.session.add(mock_buyer)
        db.session.commit()
        login_user(mock_buyer)
        client.get('/')
        response = client.get('/products/999/')
        assert response.status_code == 404

def test_read_product_by_buyer(client_buyer):
    """
    Tests that a buyer profile can read the product but does not have the option to update a product.
    """
    client, mock_buyer, mock_seller = client_buyer

    with client.application.test_request_context():
        db.session.add(mock_seller)
        db.session.commit()

        mock_product1 = Product(admin_id=mock_seller.id, name='Mock Product 1', price=9.99, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        db.session.add(mock_buyer)
        db.session.commit()

        login_user(mock_buyer)

        response = client.get('/products/1/')
        assert response.status_code == 200
        assert mock_product1.name in response.get_data(as_text=True)
        assert "Update Product" not in response.get_data(as_text=True)

def test_read_product_by_seller(client_seller):
    """
    Tests that a seller profile can read the product and has the option to update a product
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():

        db.session.add(mock_seller)
        db.session.commit()

        login_user(mock_seller)

        mock_product1 = Product(admin_id=current_user.id, name='Mock Product 1', price=9.99, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        response = client.get('/products/1/')
        assert response.status_code == 200
        assert mock_product1.name in response.get_data(as_text=True)
        assert "Update Product" in response.get_data(as_text=True)

def test_update_product_by_seller(client_seller):
    """
    Tests that a seller profile can update a product.
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():

        db.session.add(mock_seller)
        db.session.commit()

        login_user(mock_seller)

        mock_product1 = Product(admin_id=current_user.id, name='Mock Product 1', price=9.99, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        client.post('products/1/update',
        data={
            'name': 'Updated Mock Product',
            'price': 10.99,
            'stock': 35,
            'description': 'This is a first mock product to be updated.',
            'image': 'https://example.com/image_update.png'}
        )
        response = client.get('/products/1/')
        assert response.status_code == 200
        assert "Updated Mock Product" in response.get_data(as_text=True)
        assert "This is a first mock product to be updated." in response.get_data(as_text=True)
        assert "10.99" in response.get_data(as_text=True)
        assert "35" in response.get_data(as_text=True)
        assert "https://example.com/image_update.png" in response.get_data(as_text=True)

def test_delete_product_by_seller(client_seller):
    """
    Tests that a seller can delete its own product and check that the specific is no longer in the home page.
    """
    client, mock_seller = client_seller
    with client.application.test_request_context():

        db.session.add(mock_seller)
        db.session.commit()

        login_user(mock_seller)

        mock_product1 = Product(admin_id=current_user.id, name='Mock Product 1', price=9.99, stock=30, description='This is a first mock product.', image='https://example.com/image1.png',)
        db.session.add(mock_product1)
        db.session.commit()

        mock_product2 = Product(admin_id=current_user.id, name='Mock Product 2', price=9.99, stock=40, description='This is a second mock product.', image='https://example.com/image2.png',)
        db.session.add(mock_product2)
        db.session.commit()
        client.get('products/2/update')
        client.post('products/delete', data={'product_id': 2})
        response = client.get('/')
        assert response.status_code == 200
        assert mock_product1.name in response.get_data(as_text=True)
        assert mock_product2.name not in response.get_data(as_text=True)
        assert client.get('/product/2').status_code == 404
