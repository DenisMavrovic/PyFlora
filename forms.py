from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo



class RegistrationForm(FlaskForm):
    first_name = StringField('Ime', validators=[DataRequired(message='Polje za unos imena je obvezno!')])
    last_name = StringField('Prezime', validators=[DataRequired()])
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    confirm_password = PasswordField('Ponovite lozinku', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Dalje')

class LoginForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired()])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    submit = SubmitField('PRIJAVA')

class PyPot(FlaskForm):
    name = StringField('Naziv posude', validators=[DataRequired()])
    location = StringField('Lokacija', validators=[DataRequired()])
    flower = StringField('Cvijet')    
    submit = SubmitField('Dodajte novu posudu')
    discard = SubmitField('ODUSTANI')

class UpdatePyPot(FlaskForm):
    name = StringField('Naziv posude')
    location = StringField('Lokacija')
    flower = StringField('Cvijet')    
    submit = SubmitField('Ažuriraj')
    discard = SubmitField('ODUSTANI')

class AddFlower(FlaskForm):
    flower_name = StringField('Naziv biljke', validators=[DataRequired()])
    soil_humidity = DecimalField('Vlažnost tla', validators=[DataRequired()])
    soil_ph = DecimalField('pH vrijednost', validators=[DataRequired()])    
    soil_salinity = DecimalField('Salinitet', validators=[DataRequired()])    
    env_temperature = DecimalField('Temperatura zraka', validators=[DataRequired()])    
    light_intensity = DecimalField('Razina svjetla', validators=[DataRequired()])
    flower_img = FileField('Slika biljke (Format slike: jpg, png)', validators=[FileAllowed(['jpg', 'png'])])    
    submit = SubmitField('Dodajte novu biljku')
    discard = SubmitField('ODUSTANI')

class UpdateFlower(FlaskForm):
    flower_name = StringField('Naziv biljke', validators=[DataRequired()])
    soil_humidity = DecimalField('Vlažnost tla', validators=[DataRequired()])
    soil_ph = DecimalField('pH vrijednost', validators=[DataRequired()])    
    soil_salinity = DecimalField('Salinitet', validators=[DataRequired()])    
    env_temperature = DecimalField('Temperatura zraka', validators=[DataRequired()])    
    light_intensity = DecimalField('Razina svjetla', validators=[DataRequired()])
    flower_img = FileField('Slika biljke (Format slike: jpg, png)', validators=[FileAllowed(['jpg', 'png'])])    
    submit = SubmitField('Ažuriraj')
    discard = SubmitField('ODUSTANI')

class UpdateAccountForm(FlaskForm):
    first_name = StringField('Ime', validators=[DataRequired(message='Polje za unos imena je obvezno!')])
    last_name = StringField('Prezime', validators=[DataRequired()])
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Ažuriraj')

# add_substrate = BooleanField('Preporuka za dodavanje supstrata', validators=[DataRequired()])    