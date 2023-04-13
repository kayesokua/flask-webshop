from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, Email, Length, NumberRange, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from email_validator import validate_email, EmailNotValidError
from application.extensions.db import db
from application.models import User
from wtforms.widgets import Select


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_on_submit(self):
        if not super(LoginForm, self).validate_on_submit():
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user or not check_password_hash(user.password, self.password.data):
            self.username.errors.append('Invalid username or password')
            return False
        db.session.add(user)
        db.session.commit()
        return login_user(user)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, message='Please make sure your username has at least 6 characters and only contains letters, numbers, and underscore.'), Regexp('^\w+$', message='Please make sure your username has at least 6 characters and only contains letters, numbers, and underscore.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Please make sure your password has at least 6 characters.'), Regexp('^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{6,}$', message='Please make sure your password contains at least 1 number and 1 symbol.')])
    password2 = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')])
    accept_tos = BooleanField('I accept Terms of Service and Privacy Policy. If left unchecked, no orders can be completed', validators=[DataRequired(message='You must accept the Terms of Service and Privacy Policy to register.')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already taken.')

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False
        else:
            user = User(
                username=self.username.data,
                password=generate_password_hash(self.password.data),
                is_active=True,
                is_admin=False,
                accept_tos=self.accept_tos.data)
            db.session.add(user)
            db.session.commit()
            return login_user(user)

class DeliveryForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=255)], render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=255)], render_kw={"placeholder": "Last Name"})
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)], render_kw={"placeholder": "Email"})
    delivery_house_nr = StringField('House Number', validators=[DataRequired(), Length(max=10)], render_kw={"placeholder": "House Number"})
    delivery_street = StringField('Street', validators=[DataRequired(), Length(max=50)], render_kw={"placeholder": "Street"})
    delivery_additional = StringField('Additional Address (Optional)', validators=[Length(max=255)], render_kw={"placeholder": "Additional Address"})
    delivery_state = StringField('State', validators=[DataRequired(), Length(max=50)],  render_kw={"placeholder": "State"})
    delivery_postal = StringField('Postal Code', validators=[DataRequired(), Length(max=10)], render_kw={"placeholder": "Postal Code"})
    delivery_country = SelectField('Country', validators=[DataRequired()], choices=[('AT', 'Austria'), ('BE', 'Belgium'), ('BG', 'Bulgaria'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'),
                    ('DE', 'Germany'), ('DK', 'Denmark'), ('EE', 'Estonia'), ('ES', 'Spain'), ('FI', 'Finland'),
                    ('FR', 'France'), ('GR', 'Greece'), ('HR', 'Croatia'), ('HU', 'Hungary'), ('IE', 'Ireland'),
                    ('IT', 'Italy'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('MT', 'Malta'),
                    ('NL', 'Netherlands'), ('PL', 'Poland'), ('PT', 'Portugal'), ('RO', 'Romania'), ('SE', 'Sweden'),
                    ('SI', 'Slovenia'), ('SK', 'Slovakia')], render_kw={"placeholder": "Select Country"})
    instructions = TextAreaField('Additional Instructions (Optional)', validators=[Length(max=255)], render_kw={"placeholder": "Ex. Please leave it at the reception"})
    submit = SubmitField('Save')

    def __init__(self, delivery_address=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = delivery_address

    def validate_email(self, email):
        try:
            valid_email = validate_email(email.data)
            email.data = valid_email.email
        except EmailNotValidError as e:
            raise ValidationError(str(e))
