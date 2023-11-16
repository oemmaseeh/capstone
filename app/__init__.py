from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from app.forms import ProductForm, RegistrationForm
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import psycopg2

conn = psycopg2.connect(
    dbname='capstone project',
    user='elhlgvnb',
    password='p39xLdV11dJAD22YvORSKFYoL8VjPQN3',
    host='bubble.db',
    port='p39'
)

products = []

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'  
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://elhlgvnb:p39xLdV11dJAD22YvORSKFYoL8VjPQN3@bubble.db.elephantsql.com/elhlgvnb'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.config['FLASK_DEBUG'] = 1
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    products_sold = db.relationship('Product', backref='owner', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('products', lazy=True))


@app.route('/')
def homepage():
    return render_template('index.html', products=products)

from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(app.config['SQLALCHEMY_DATABASE_URI'])

        return redirect(url_for('login'))


    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials. Try again.')
    return render_template('login.html')

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = ProductForm()

    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            seller_id=session['user_id']
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('sell.html', form=form)


@app.route('/logout')
def logout():
    # Remove the user_id from the session if it's there
    session.pop('user_id', None)
    # Redirect to the login page or any other desired page after logout
    return redirect(url_for('login'))


@app.route('/buy/<int:product_id>')
def buy(product_id):
    
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return f"You have purchased {product['name']} for ${product['price']}."
    else:
        return "Product not found."


    

@app.route('/dashboard')
def dashboard():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_table")
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('dashboard.html', data=data)



if __name__ == '__main__':
    app.run()