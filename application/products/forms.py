from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange, URL
import re
from application.models import Product
from application.extensions.db import db
from flask_login import current_user

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=5, max=50)])
    price = FloatField('Price (€)', validators=[DataRequired(), NumberRange(min=0.5, max=99)], render_kw={"placeholder": "€0,50"})
    stock = IntegerField('Stock (Qty.)', validators=[DataRequired(), NumberRange(min=10)], render_kw={"placeholder": "10"})
    image = StringField('Image URL', validators=[DataRequired(), URL(require_tld=True, message="Please enter a valid URL starting with 'https://'")], render_kw={"placeholder": "https://example.com/image.jpg"})
    description = TextAreaField('Product Description', validators=[DataRequired(), Length(min=10, max=250)], render_kw={"placeholder": "Tell us about the product."})

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

    def validate_name(self, name):
        """
        If the form is being used to update an existing product and the
        name hasn't changed, we don't need to do any validation
        """
        if self.product is not None and self.product.name == name.data:
            return

        search_result = Product.query.filter_by(name=name.data).first()
        if search_result is not None:
            raise ValidationError('This product name is already taken.')