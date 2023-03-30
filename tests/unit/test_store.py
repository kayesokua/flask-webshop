import json
import pytest


def test_index(test_app_with_db):
    response = test_app_with_db.get('/')
    assert response.status_code == 200

def test_get_product_by_admin(test_app_with_db):
    pass


def test_get_product_by_id(test_app_with_db):
    pass


def test_add_product_incorrect_id(test_app_with_db):
    pass


def test_update_product(test_app_with_db):
    pass


def test_delete_product(test_app_with_db):
    pass


def test_get_product_incorrect_id(test_app_with_db):
    response = test_app_with_db.get('/product/999')
    assert response.status_code == 404
    assert response.json['detail'] == 'Product not found'

def test_handle_cart(test_app_with_db):
    pass


def test_cart_add_item(test_app_with_db):
    pass


def test_cart_remove_item(test_app_with_db):
    pass


def test_create_checkout_session(test_app_with_db):
    pass


def test_strip_webhook(test_app_with_db):
    pass
