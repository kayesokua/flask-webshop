from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, Email, ValidationError
from flask_login import login_user
from email_validator import validate_email, EmailNotValidError
from application.extensions.db import db
from application.models import User
import bcrypt
from flask import request, flash, redirect, url_for
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_on_submit(self):
        if not super().validate_on_submit():
            flash('Something went wrong. Please try again', 'danger')
            return False
        else:
            user = User.query.filter_by(username=self.username.data).first()
            if not user:
                flash('Invalid username or password')
                return False

            if not user.is_active:
                flash('User has been deactivated. Please contact support to reactivate.')
                return False

            check_password = bcrypt.checkpw(self.password.data.encode('utf-8'), user.hashed_password)

            if not check_password:
                flash('Invalid username or password')
                return False

            user.last_signed_in_ip = request.remote_addr
            user.last_signed_in = datetime.utcnow()
            user.login_count += 1
            db.session.commit()

            return login_user(user)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, message='Please make sure your username has at least 6 characters and only contains letters, numbers, and underscore.'), Regexp('^\w+$', message='Please make sure your username has at least 6 characters and only contains letters, numbers, and underscore.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Please make sure your password has at least 6 characters.'), Regexp('^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{6,}$', message='Please make sure your password contains at least 1 number and 1 symbol.')])
    password2 = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')])
    accept_tos = BooleanField('I accept the Terms of Service', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already taken.')

    def validate_on_submit(self):
        if not super().validate_on_submit():
            flash('Something went wrong. Please try again', 'danger')
            return False
        else:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(self.password.data.encode('utf-8'), salt)
            user = User(
                username=self.username.data,
                hashed_password=hashed_password,
                salt=salt,
                last_password_change=datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully. Please login.', 'success')
            return redirect(url_for('accounts.login'))

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

class ChangePasswordForm(FlaskForm):
    confirm_password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
    new_password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "New Password"})
    new_password2 = PasswordField('Confirm Password', validators=[EqualTo('new_password', message='Passwords must match.')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Submit')

    def validate_on_submit(self, current_user):
        if not super().validate():
            flash('Something went wrong', 'danger')
            return False
        check_password = bcrypt.checkpw(self.confirm_password.data.encode('utf-8'), current_user.hashed_password)
        if not check_password:
            flash('Invalid password', 'danger')
            return False
        elif self.new_password.data == current_user.hashed_password:
            flash('New password cannot be the same as the old password', 'danger')
            return False
        return True

class ChangeMobileForm(FlaskForm):
    country_code = SelectField('Country', validators=[DataRequired()],
                               choices=[('43', '🇦🇹 +43'), ('32', '🇧🇪 +32'), ('359', '🇧🇬 +359'), ('357', '🇨🇾 +357'), ('420', '🇨🇿 +420'),
                                        ('49', '🇩🇪 +49'), ('45', '🇩🇰 +45'), ('372', '🇪🇪 +372'), ('34', '🇪🇸 +34'), ('358', '🇫🇮 +358'),
                                        ('33', '🇫🇷 +33'), ('30', '🇬🇷 +30'), ('385', '🇭🇷 +385'), ('36', '🇭🇺 +36'), ('353', '🇮🇪 +353'),
                                        ('39', '🇮🇹 +39'), ('370', '🇱🇹 +370'), ('352', '🇱🇺 +352'), ('371', '🇱🇻 +371'), ('356', '🇲🇹 +356'),
                                        ('31', '🇳🇱 +31'), ('48', '🇵🇱 +48'), ('351', '🇵🇹 +351'), ('40', '🇷🇴 +40'), ('46', '🇸🇪 +46'),
                                        ('386', '🇸🇮 +386'), ('421', '🇸🇰 +421')], render_kw={"placeholder": "Select Country"})
    mobile_code = StringField('Mobile Number', validators=[DataRequired()], render_kw={"placeholder": "Mobile Number"})
    submit = SubmitField('Submit')

    def validate_on_submit(self):
        if not super().validate():
            flash('Something went wrong', 'danger')
            return False
        mobile = f"+{self.country_code.data}{self.mobile_code.data}"
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already exists', 'danger')
            return False
        return True

class VerifyMobileForm(FlaskForm):
    verification_token = StringField('Verification Code', validators=[DataRequired(), Length(min=6,max=6)], render_kw={"placeholder": "Verification Code"})
    submit = SubmitField('Submit')

    def validate_on_submit(self, current_user):
        if not super().validate():
            flash('Something went wrong', 'danger')
            return False
        if not current_user.mobile:
            flash('Please add a mobile number first', 'danger')
            return False
        return True