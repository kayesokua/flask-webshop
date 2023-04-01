from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField, SelectField,RadioField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from email_validator import validate_email, EmailNotValidError
from application.models.accounts import DeliveryAddress

class CheckoutForm(FlaskForm):
    selected_address = RadioField('Delivery Address', validators=[DataRequired()], coerce=int)
    checkout = SubmitField('Confirm Order')

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        addresses = DeliveryAddress.query.filter_by(user_id=current_user.id).order_by(DeliveryAddress.delivery_street.asc()).all()
        choices = []
        for address in addresses:
            choices.append(address.id)
        self.selected_address.choices = choices

class OrderStatusForm(FlaskForm):
    delivery_status = SelectField('Delivery Status', validators=[DataRequired()], choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('received', 'Received'),
        ('disrupted', 'Disrupted'),
        ('lost', 'Lost')
    ])
    stripe_payment_id = StringField('Stripe Payment ID', validators=[DataRequired(), Length(max=255)], render_kw={"placeholder": "Stripe Payment ID"})
    submit = SubmitField('Confirm Order')