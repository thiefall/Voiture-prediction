from flask import Flask, request, render_template, redirect, url_for, session
from joblib import load
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# Lod the model
model = load('elastic_poly_model.joblib')

app = Flask(__name__)
app.secret_key = 'Very secret' #To secure the sessions

# default id
#USERNAME = "client"
#PASSWORD = "1234"

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS car (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symboling INT,
            fueltype TEXT,
            aspiration TEXT,
            doornumber TEXT,
            carbody TEXT,
            drivewheel TEXT,
            enginelocation TEXT,
            wheelbase FLOAT,
            carlength FLOAT,
            carwidth FLOAT,
            carheight FLOAT,
            curbweight INT,
            enginetype TEXT,
            cylindernumber TEXT,
            enginesize INT,
            fuelsystem TEXT,
            boreratio FLOAT,
            stroke FLOAT,
            compressionratio FLOAT,
            horsepower INT,
            peakrpm TEXT,
            citympg TEXT,
            highwaympg TEXT,
            CarBrand TEXT,
            prediction FLOAT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')
        conn.commit()

# Run DB init at app startup
init_db()

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "Username already exists."
    
    return render_template('signup.html', error=error)


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home_page'))
        else:
            error = "Incorrect credentials."

    return render_template('login.html', error=error)


@app.route("/index", methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    prediction = None
    car_data = None
    username = session.get('username')
    
    if request.method == 'POST':
        try:
            # Retrieve the form data
            car_features = {
                "symboling": int(request.form['symboling']),
                "fueltype": request.form["fueltype"],
                "aspiration": request.form["aspiration"],
                "doornumber": request.form["doornumber"],
                "carbody": request.form["carbody"],
                "drivewheel": request.form["drivewheel"],
                "enginelocation": request.form["enginelocation"],
                "wheelbase": float(request.form["wheelbase"]),
                "carlength": float(request.form["carlength"]),
                "carwidth": float(request.form["carwidth"]),
                "carheight": float(request.form["carheight"]),
                "curbweight": int(request.form["curbweight"]),
                "enginetype": request.form["enginetype"],
                "cylindernumber": request.form["cylindernumber"],
                "enginesize": int(request.form["enginesize"]),
                "fuelsystem": request.form["fuelsystem"],
                "boreratio": float(request.form["boreratio"]),
                "stroke": float(request.form["stroke"]),
                "compressionratio": float(request.form["compressionratio"]),
                "horsepower": int(request.form["horsepower"]),
                "peakrpm": request.form["peakrpm"],
                "citympg": request.form["citympg"],
                "highwaympg": request.form["highwaympg"],
                "CarBrand": request.form["CarBrand"]
            } 

            #Conversion in DF
            input_df = pd.DataFrame([car_features])

            # Prediction
            prediction = model.predict(input_df)[0]
            prediction = round(prediction, 2)
            car_features['prediction'] = prediction

            with sqlite3.connect('database.db') as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO car (
                    symboling, fueltype, aspiration, doornumber, carbody, drivewheel, enginelocation,
                    wheelbase, carlength, carwidth, carheight, curbweight, enginetype, cylindernumber,
                    enginesize, fuelsystem, boreratio, stroke, compressionratio, horsepower, peakrpm,
                    citympg, highwaympg, CarBrand, prediction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (*car_features.values(),))
                conn.commit()

            
            return render_template('index.html', prediction=prediction)
        
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html', username=username)

@app.route('/help')
def help():
    username = session.get('username')
    return render_template('help.html', username=username)

@app.route('/about')
def about():
    username = session.get('username')
    return render_template('about.html', username=username)

@app.route('/home')
def home_page(): 
    generate_statistics()
    username = session.get('username')
    return render_template('home.html', username=username)                           

    
def generate_statistics():
    # Chargement du dataset d'origine
    df = pd.read_csv('CarPrice_Assignment.csv')

    os.makedirs("static/plots", exist_ok=True)

    # Top 10 marques les plus fréquentes
    top_brands = df['CarName'].value_counts().head(10)
    plt.figure(figsize=(10,5))
    top_brands.plot(kind='bar', color='skyblue')
    plt.title("Top 10 des marques de voiture")
    plt.ylabel("Nombre d'entrées")
    plt.tight_layout()
    plt.savefig("static/plots/top10_brands.png")
    plt.close()

    # Prix moyen par marque
    mean_prices = df.groupby('CarName')['price'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10,5))
    mean_prices.plot(kind='bar', color='orange')
    plt.title("Prix moyen par marque (Top 10)")
    plt.ylabel("Prix moyen ($)")
    plt.tight_layout()
    plt.savefig("static/plots/mean_price_per_brand.png")
    plt.close()

    # Pie chart du type de carburant
    fuel_counts = df['fueltype'].value_counts()
    plt.figure(figsize=(6,6))
    plt.pie(fuel_counts, labels=fuel_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66b3ff','#ff9999','#99ff99','#ffcc99'])
    plt.title("Répartition des types de carburant")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig("static/plots/fueltype_pie.png")
    plt.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


