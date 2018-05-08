from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Accepts a nickname and a room."""

    name = StringField('Name', validators=[DataRequired()])
    team = RadioField('Team', choices=[('team-a', 'Team A'), ('team-b', 'Team B')], validators=[DataRequired()])  # TODO: funny names?
    submit = SubmitField('Start!')
