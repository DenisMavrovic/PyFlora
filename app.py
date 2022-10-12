import os 
import secrets
import random
from PIL import Image
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm, PyPot, AddFlower, UpdateAccountForm, UpdateFlower, UpdatePyPot
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from repository import get_weather


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fe4984c8f13649cee67dc16406e49e9fa8ea'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/pyflora.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Prijevite se za pristup stranici!'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    plant_pot = db.relationship('PyFloraPot', backref='user', lazy=True)

class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flower_name = db.Column(db.String(100), unique=True, nullable=False)
    flower_img = db.Column(db.String(20), unique=True, nullable=False, default='default.jpg')
    soil_humidity = db.Column(db.Float())
    soil_ph = db.Column(db.Float())
    soil_salinity = db.Column(db.Float())
    env_temperature = db.Column(db.Float())
    light_intensity = db.Column(db.Float())
    plant_pot = db.relationship('PyFloraPot', backref='flower', lazy=True)

class PyFloraPot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pot_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    time_stamp = db.Column(db.DateTime(), default=datetime.utcnow())
    air_temperature = db.Column(db.Float())
    add_substrate = db.Column(db.Boolean())
    flower_id = db.Column(db.String(100), db.ForeignKey('flower.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Sync(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.Integer)
    pH = db.Column(db.Float())
    salinity = db.Column(db.Float())
    temp = db.Column(db.Float())
    light_intensity = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime(), default=datetime.utcnow())

now = datetime.now()
h = now.strftime("%H")
h = int(h)

weather = get_weather()

def generator():
    humidity = 30
    pH = 6.3
    temp = 22
    salinity = 6.2
    humidity = humidity + random.randint(-5, 5)
    rnd_int = random.choice(range(1, 9))
    print(rnd_int)
    rnd_float = rnd_int/10
    pH = round(pH + rnd_float, 1)
    temp = weather["main"]["temp"]
    if h in range(6, 15):
        light_intensity = random.randrange(400, 110000)
    if h in range(14, 19):
        light_intensity = random.randrange(400, 110000)
    if h in range(20, 24) or h in range(0, 7):
        light_intensity = random.randrange(1, 400)
    return humidity, pH, temp, salinity, light_intensity

@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('pyposude'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('pyposude'))
        else:
            flash('Prijava nije uspjela. Ponovno upišite korisničko ime i lozinku.', 'danger')
    return render_template('index.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pyposude'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Račun za korisnika {form.username.data} je uspješno kreiran! Možete se prijaviti.', 'success')    
        return redirect(url_for('index'))
    return render_template('register.html', title='Novi Račun', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/sync", methods=['POST'])
@login_required
def sync():
    humidity, pH, temp, salinity, light_intensity = generator()
    g_vals = Sync(humidity=humidity, pH=pH, salinity=salinity, temp=temp, light_intensity=int(light_intensity))
    db.session.add(g_vals)
    db.session.commit()
    flash('Podaci su spremljeni!', 'success')
    return redirect(url_for('pyposude'))

@app.route("/dodavanje_posude", methods=['GET', 'POST'])
@login_required
def dodavanje_posude():
    form = PyPot()
    if form.validate_on_submit():
        pyflower = Flower.query.filter_by(flower_name=form.flower.data).first()
        py_pot = PyFloraPot(pot_name=form.name.data, location=form.location.data, flower_id=pyflower.id, user=current_user)
        db.session.add(py_pot)
        db.session.commit()
        flash(f'Nova PyPosuda {form.name.data} je dodana!', 'success')
        return redirect(url_for('pyposude'))
    return render_template('dodavanje_posude.html', title='Dodavanje Pyposude', form=form)

@app.route("/pyposude")
def pyposude():
    pypots = PyFloraPot.query.filter_by(user=current_user).all()    
    return render_template('pyposude.html', pypots=pypots)

@app.route("/obrisi_posudu", methods=['POST'])
@login_required
def obrisi_posudu():
    pot_id = request.args.get('pot_id')
    py_pot = PyFloraPot.query.get(pot_id)
    db.session.delete(py_pot)
    db.session.commit()
    flash('Posuda je obrisana!', 'success')
    return redirect(url_for('pyposude'))

# @app.route("/biljka")
# @login_required
# def biljka():
#     flower_id = request.args.get('flower_id')
#     pyflower = Flower.query.get(flower_id)
#     return render_template('biljka.html', title='Biljka', pyflower=pyflower)

@app.route("/biljka/<int:flower_id>")
@login_required
def biljka(flower_id):
    pyflower = Flower.query.get(flower_id)
    return render_template('biljka.html', title='Biljka', pyflower=pyflower)

@app.route("/biljke")
@login_required
def biljke():
    pyflowers = Flower.query.all()
    return render_template('biljke.html', title='Biljke', pyflowers=pyflowers)

def save_img(form_img):
    rnd_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_img.filename)
    img_name = rnd_hex + file_ext
    img_path = os.path.join(app.root_path, 'static/assets/biljke', img_name)

    img_size = (500, 500)
    img = Image.open(form_img)
    img.thumbnail(img_size)
    img.save(img_path)    

    return img_name

@app.route("/dodavanje_biljke", methods=['GET', 'POST'])
@login_required
def dodavanje_biljke():
    form = AddFlower()
    if form.validate_on_submit():
        if form.flower_img.data:
            img_file = save_img(form.flower_img.data)            
        py_flower = Flower(flower_name=form.flower_name.data, flower_img=img_file, soil_humidity=form.soil_humidity.data, soil_ph=form.soil_ph.data, soil_salinity=form.soil_salinity.data, env_temperature=form.env_temperature.data, light_intensity=form.light_intensity.data)
        db.session.add(py_flower)
        db.session.commit()
        flash(f'Nova biljka je dodana!', 'success')
        return redirect(url_for('biljke'))
    return render_template('dodavanje_biljke.html', title='Dodavanje Biljke', form=form)

@app.route("/azuriranje_biljke/<int:flower_id>", methods=['GET', 'POST'])
@login_required
def azuriranje_biljke(flower_id):
    pyflower = Flower.query.get(flower_id)
    form = UpdateFlower()
    if form.validate_on_submit():
        if form.flower_img.data:
            img_file = save_img(form.flower_img.data)
            pyflower.flower_img = img_file
        pyflower.flower_name = form.flower_name.data
        pyflower.soil_humidity = form.soil_humidity.data
        pyflower.soil_ph = form.soil_ph.data
        pyflower.soil_salinity = form.soil_salinity.data
        pyflower.env_temperature = form.env_temperature.data
        pyflower.light_intensity = form.light_intensity.data        
        db.session.commit()
        flash('Podaci su ažurirani!', 'success')
        return redirect(url_for('biljka', flower_id=pyflower.id))
    elif request.method == 'GET':
        form.flower_name.data = pyflower.flower_name
        form.soil_humidity.data = pyflower.soil_humidity
        form.soil_ph.data = pyflower.soil_ph
        form.soil_salinity.data = pyflower.soil_salinity
        form.env_temperature.data = pyflower.env_temperature
        form.light_intensity.data = pyflower.light_intensity
    return render_template('azuriranje_biljke.html', title='Ažuriranje podataka', form=form, pyflower=pyflower)

@app.route("/obrisi_biljku", methods=['POST'])
@login_required
def obrisi_biljku():
    flower_id = request.args.get('flower_id')
    pyflower = Flower.query.get(flower_id)
    db.session.delete(pyflower)
    db.session.commit()
    flash('Biljka je obrisana!', 'success')
    return redirect(url_for('biljke'))

# @app.route("/posuda/<user_id>", methods=['GET', 'POST'])
# @login_required
# def posuda(user_id):
#     print(user_id)
#     # py_pot = PyFloraPot.query.get(pot_id)
#     return render_template('posuda.html', title='Posuda')

@app.route("/posuda")
@login_required
def posuda():
    vals = Sync.query.all()
    labels = []
    values = []
    for val in vals:
        labels.append(val.time_stamp.strftime("%d/%m/%Y %H:%M:%S"))
        values.append(val.temp)
    pot_id = request.args.get('pot_id')
    flower_id = request.args.get('flower_id')
    pypot = PyFloraPot.query.get(pot_id)
    pyflower = Flower.query.get(flower_id)
    val = Sync.query.order_by(Sync.id.desc()).first()
    return render_template('posuda.html', title='Posuda', pypot=pypot, pyflower=pyflower, val=val, labels=labels, values=values)

@app.route("/azuriranje_posude/<int:pot_id>", methods=['GET', 'POST'])
@login_required
def azuriranje_posude(pot_id):
    pypot = PyFloraPot.query.get(pot_id)
    form = UpdatePyPot()
    if form.validate_on_submit():
        pypot.pot_name = form.name.data,
        pypot.location = form.location.data       
        db.session.commit()
        flash('Podaci su ažurirani!', 'success')
        return redirect(url_for('posuda', pypot_id=pypot.id))
    elif request.method == 'GET':
        form.name.data = pypot.pot_name
        form.location.data = pypot.location
    return render_template('azuriranje_posude.html', title='Ažuriranje podataka', form=form, pypot=pypot)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data 
        current_user.last_name = form.last_name.data 
        current_user.username = form.username.data 
        db.session.commit()
        flash('Vaš račun je ažuriran!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name 
        form.username.data = current_user.username 
    return render_template('account.html', title='Moj profil', form=form)


if __name__ == '__main__':
    app.run(debug=True)