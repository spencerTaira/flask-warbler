
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, InputRequired, \
    Optional, URL, ValidationError

def check_if_image(form,field):
    """ Check if string ends with .jpg or .png
        Raise validation error if does not satisfy condition
    """

    if not(field.data.endswith(".jpg") or field.data.endswith(".png")):
        raise ValidationError("Enter Valid Image URL") #NOTE: Checking extensions on image url


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class EditUserForm(FlaskForm):
    """ Edit User Profile Form """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('Image URL', validators=[Optional(), check_if_image])
    header_image_url = StringField(
        'Header Image URL',
        validators=[Optional(),
        check_if_image]
    )
    bio = TextAreaField('Bio', validators=[Optional()])
    password = PasswordField('Password', validators=[InputRequired()])


class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

