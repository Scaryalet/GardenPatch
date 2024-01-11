#Imports necessary classes/modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os


#Creates Flask App
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'GardenPatch/uploads/seed_images'
#Where the database to connect to is n n  bnn gbg/bb/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
#Choose a secret key
app.config["SECRET_KEY"] = "GPKey"
#Initialize the database
db = SQLAlchemy()

#Set up the Login Manager
#This is needed so users can log in and out
login_manager = LoginManager()
login_manager.init_app(app)

#To store user information, a table needs to be created. 
#Create User class and make it a subclass of db.Model.
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    hemisphere = db.Column(db.String(20), nullable=False)
    # Add a relationship to connect users to their seeds
    seeds = db.relationship('Seed', backref='user', lazy=True)

#Create Seed class, make it a subclass of db.Model
class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    plant_type = db.Column(db.String(250), nullable=False)
    germinate_time = db.Column(db.String(250))
    planting_depth = db.Column(db.String(250))
    plant_spacing = db.Column(db.String(250))
    maturity_time = db.Column(db.String(250))
    sun_requirement = db.Column(db.String(250))
    when_to_plant = db.Column(db.String(250))
    image_filename = db.Column(db.String(255))

#Initializes Flask-SQLAlchemy extension with flask App.
db.init_app(app)

#Then create the database table
with app.app_context():
    db.create_all()

#User loader callback, returns user object from id
@login_manager.user_loader
def loader_user(user_id) :
        return Users.query.get(user_id)

# Define the helper function to save image
def save_image(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None


#Routes for the Web App
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/account/")
def account():
    return render_template("account.html")

@app.route('/loginregister/')
def loginregister():        
    return render_template("loginregister.html")

# Registration form display
@app.route('/register', methods=["GET"])
def show_register_form():
    return render_template("loginregister.html")

# Registration route
@app.route('/register', methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form.get("regUsername")
        password = request.form.get("regPassword")
        confirm_password = request.form.get("confirmPassword")
        hemisphere = request.form.get("hemisphere")

        # Check if password and confirm password match
        if password != confirm_password:
            return render_template("loginregister.html")

        # Check if the username is already taken
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return render_template("loginregister.html")

        # Create a new user
        user = Users(username=username, password=password, hemisphere=hemisphere)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("home"))
    
# Login form display
@app.route('/login', methods=["GET"])
def show_login_form():
    return render_template("loginregister.html")
  
# Login route
@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))

    return render_template("loginregister.html")

@app.route("/seedlibrary/")
def seedLibrary():
    return render_template("seedLibrary.html")

@app.route("/myPlants/")
def myPlants():
    return render_template("myPlants.html")

@app.route("/tasks/")
def tasks():
    return render_template("tasks.html")

@app.route("/calendar/")
def calendar():
    return render_template("calendar.html")

# Route for adding seed form submission
@app.route('/add_seed', methods=['POST'])
@login_required  # Ensure that the user is logged in
def add_seed():
    seed_name = request.form.get('addSeedName')
    plant_type = request.form.get('addSeedType')
    germinate_time = request.form.get('addSeedGermination')
    planting_depth = request.form.get('addSeedDepth')
    plant_spacing = request.form.get('addSeedSpacing')
    maturity_time = request.form.get('addSeedMaturity')
    sun_requirement = request.form.get('addSeedSun')
    when_to_plant = request.form.get('addSeedSeason')
    
    # Get the image file
    image_file = request.files.get('addSeedImage')

    # Save the image file
    image_filename = save_image(image_file)

    # Create a new seed with the form data
    new_seed = Seed(
        name=seed_name,
        plant_type=plant_type,
        germinate_time=germinate_time,
        planting_depth=planting_depth,
        plant_spacing=plant_spacing,
        maturity_time=maturity_time,
        sun_requirement=sun_requirement,
        when_to_plant=when_to_plant,
        image_filename=image_filename
    )

    # Add the new seed to the database
    db.session.add(new_seed)
    db.session.commit()

    # Redirect to the seed library page or render a template
    return redirect(url_for('seedLibrary'))
