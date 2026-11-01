import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'petpaglus_secret'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'petpaglus.db')
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'saketh@123',
    'database': 'petpaglus_db'
}


def is_sqlite_connection(conn):
    return isinstance(conn, sqlite3.Connection)


def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS shelters (
            shelter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            contact TEXT
        );

        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            age TEXT NOT NULL,
            status TEXT DEFAULT 'available',
            shelter_id INTEGER,
            FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id)
        );

        CREATE TABLE IF NOT EXISTS adopters (
            adopter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS adoption (
            adoption_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            adopter_id INTEGER,
            adoption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
            FOREIGN KEY (adopter_id) REFERENCES adopters(adopter_id)
        );

        CREATE TABLE IF NOT EXISTS vaccinations (
            vaccination_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            vaccine_name TEXT,
            vaccination_date TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
        );

        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            shelter_id INTEGER,
            FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id)
        );
    ''')

    if conn.execute('SELECT COUNT(*) FROM shelters').fetchone()[0] == 0:
        shelters = [
            ('Happy Tails Shelter', 'Hyderabad', '9999999999'),
            ('Paws Care Center', 'Vijayawada', '8888888888')
        ]
        conn.executemany(
            'INSERT INTO shelters (name, location, contact) VALUES (?, ?, ?)',
            shelters
        )

        pets = [
            ('Bella', 'Dog', '3 years', 'available', 1),
            ('Luna', 'Cat', '2 years', 'available', 1),
            ('Charlie', 'Dog', '5 years', 'available', 2),
            ('Milo', 'Cat', '1 year', 'adopted', 2),
        ]
        conn.executemany(
            'INSERT INTO pets (name, type, age, status, shelter_id) VALUES (?, ?, ?, ?, ?)',
            pets
        )

        conn.executemany(
            'INSERT INTO adopters (name, phone) VALUES (?, ?)',
            [('John Doe', '555-1234')]
        )

        conn.executemany(
            'INSERT INTO adoption (pet_id, adopter_id, adoption_date) VALUES (?, ?, CURRENT_TIMESTAMP)',
            [(4, 1)]
        )

        conn.executemany(
            'INSERT INTO vaccinations (pet_id, vaccine_name, vaccination_date) VALUES (?, ?, ?)',
            [(1, 'Rabies', '2024-01-10'), (2, 'Feline Distemper', '2024-02-15')]
        )

        conn.executemany(
            'INSERT INTO staff (name, role, shelter_id) VALUES (?, ?, ?)',
            [('Ravi Kumar', 'Manager', 1), ('Anita Sharma', 'Caretaker', 2)]
        )

    conn.commit()
    conn.close()


init_sqlite_db()


def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        return connection


@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed. Please check the DB_CONFIG in app.py.', 500

    try:
        cursor = conn.cursor()
        if is_sqlite_connection(conn):
            cursor.execute("SELECT * FROM pets WHERE status = 'available'")
            pets = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pets WHERE status = %s", ('available',))
            pets = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        conn.close()

    return render_template('index.html', pets=pets)


@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        pet_type = request.form.get('type')
        years = request.form.get('years', '0')
        months = request.form.get('months', '0')

        age_parts = []
        if years and int(years) > 0:
            age_parts.append(f"{years} year{'s' if int(years) != 1 else ''}")
        if months and int(months) > 0:
            age_parts.append(f"{months} month{'s' if int(months) != 1 else ''}")
        age = ', '.join(age_parts) if age_parts else '0 months'

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if is_sqlite_connection(conn):
                    cursor.execute(
                        'INSERT INTO pets (name, type, age) VALUES (?, ?, ?)',
                        (name, pet_type, age)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO pets (name, type, age) VALUES (%s, %s, %s)',
                        (name, pet_type, age)
                    )
                conn.commit()
                flash('Pet added successfully!', 'success')
                return redirect(url_for('index'))
            finally:
                cursor.close()
                conn.close()

    return render_template('add_pet.html')


@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
def adopt(pet_id):
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed.', 500

    cursor = conn.cursor()
    try:
        if is_sqlite_connection(conn):
            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pet_id,))
            pet_row = cursor.fetchone()
            pet = dict(pet_row) if pet_row else None
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM pets WHERE pet_id = %s', (pet_id,))
            pet = cursor.fetchone()

        if not pet or pet['status'] != 'available':
            flash('Pet is not available for adoption.', 'warning')
            return redirect(url_for('index'))

        if request.method == 'POST':
            adopter_name = request.form.get('adopter_name')
            phone = request.form.get('phone')

            try:
                if is_sqlite_connection(conn):
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO adopters (name, phone) VALUES (?, ?)',
                        (adopter_name, phone)
                    )
                    adopter_id = cursor.lastrowid
                    cursor.execute(
                        "UPDATE pets SET status = 'adopted' WHERE pet_id = ?",
                        (pet_id,)
                    )
                    cursor.execute(
                        'INSERT INTO adoption (pet_id, adopter_id) VALUES (?, ?)',
                        (pet_id, adopter_id)
                    )
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO adopters (name, phone) VALUES (%s, %s)',
                        (adopter_name, phone)
                    )
                    adopter_id = cursor.lastrowid
                    cursor.execute(
                        "UPDATE pets SET status = 'adopted' WHERE pet_id = %s",
                        (pet_id,)
                    )
                    cursor.execute(
                        'INSERT INTO adoption (pet_id, adopter_id) VALUES (%s, %s)',
                        (pet_id, adopter_id)
                    )

                conn.commit()
                flash('Pet adopted successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                conn.rollback()
                flash(f'An error occurred: {e}', 'danger')

        return render_template('adopt.html', pet=pet)
    finally:
        cursor.close()
        conn.close()


@app.route('/adopted')
def adopted_pets():
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed.', 500

    try:
        cursor = conn.cursor()
        if is_sqlite_connection(conn):
            cursor.execute(
                """
                SELECT p.name AS pet_name, p.type, a.name AS adopter_name, ad.adoption_date
                FROM pets p
                JOIN adoption ad ON p.pet_id = ad.pet_id
                JOIN adopters a ON ad.adopter_id = a.adopter_id
                WHERE p.status = 'adopted'
                ORDER BY ad.adoption_date DESC
                """
            )
            adopted_list = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT p.name AS pet_name, p.type, a.name AS adopter_name, ad.adoption_date
                FROM pets p
                JOIN adoption ad ON p.pet_id = ad.pet_id
                JOIN adopters a ON ad.adopter_id = a.adopter_id
                WHERE p.status = 'adopted'
                ORDER BY ad.adoption_date DESC
                """
            )
            adopted_list = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('adopted.html', adopted_list=adopted_list)


@app.route('/shelters')
def shelters():
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed.', 500

    try:
        cursor = conn.cursor()
        if is_sqlite_connection(conn):
            cursor.execute('SELECT * FROM shelters')
            shelter_list = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM shelters')
            shelter_list = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('shelters.html', shelters=shelter_list)


@app.route('/staff')
def staff():
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed.', 500

    try:
        cursor = conn.cursor()
        if is_sqlite_connection(conn):
            cursor.execute(
                """
                SELECT st.name, st.role, sh.name AS shelter_name
                FROM staff st
                LEFT JOIN shelters sh ON st.shelter_id = sh.shelter_id
                """
            )
            staff_list = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT st.name, st.role, sh.name AS shelter_name
                FROM staff st
                LEFT JOIN shelters sh ON st.shelter_id = sh.shelter_id
                """
            )
            staff_list = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('staff.html', staff_list=staff_list)


@app.route('/vaccinations')
def vaccinations():
    conn = get_db_connection()
    if not conn:
        return 'Database connection failed.', 500

    try:
        cursor = conn.cursor()
        if is_sqlite_connection(conn):
            cursor.execute(
                """
                SELECT v.vaccine_name, v.vaccination_date, p.name AS pet_name
                FROM vaccinations v
                LEFT JOIN pets p ON v.pet_id = p.pet_id
                ORDER BY v.vaccination_date DESC
                """
            )
            vaccination_list = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT v.vaccine_name, v.vaccination_date, p.name AS pet_name
                FROM vaccinations v
                LEFT JOIN pets p ON v.pet_id = p.pet_id
                ORDER BY v.vaccination_date DESC
                """
            )
            vaccination_list = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('vaccinations.html', vaccinations=vaccination_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
