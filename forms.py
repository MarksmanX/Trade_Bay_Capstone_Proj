from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, URLField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

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

# Todo Add item form
class ItemAddForm(FlaskForm):
    """Add Item form."""

    title = StringField('Title', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    image = URLField('Image URL')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    image_url = StringField('Profile Image URL', validators=[Optional()])
    submit = SubmitField('Save Changes')