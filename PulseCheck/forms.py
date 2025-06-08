from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm', validators=[EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TeamForm(FlaskForm):
    team_name = StringField('Team Name')
    invite_code = StringField('Invite Code')
    submit = SubmitField('Continue')


class TrackerForm(FlaskForm):
    blocker = TextAreaField("Any Blockers?", validators=[DataRequired()])
    mood = SelectField("Your Mood Today", choices=[
        ('1', '😞 Very Low'),
        ('2', '😐 Low'),
        ('3', '🙂 Neutral'),
        ('4', '😄 Good'),
        ('5', '🤩 Excellent')
    ], validators=[DataRequired()])

    submit = SubmitField("Submit")


class InviteForm(FlaskForm):
    email = StringField("Invite a teammate (email)", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Invite")
