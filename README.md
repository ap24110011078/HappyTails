# PETPAGLUS - Pet Adoption Management System

A beginner-friendly, full-stack pet adoption platform built with Python, Flask, MySQL, HTML, and CSS. Features a clean, light pink aesthetic.

## Folder Structure

```
DBMS PROJECT/
│
├── app.py                  # Main Flask application and routes
├── database.sql            # MySQL database schema and sample data setup
├── README.md               # Setup instructions
│
├── static/
│   └── css/
│       └── style.css       # Clean, light pink UI theme
│
└── templates/
    ├── base.html           # Main shared layout
    ├── index.html          # View available pets
    ├── add_pet.html        # Form to add new pets
    ├── adopt.html          # Form for adoption details
    └── adopted.html        # View past adopted pets
```

## Setup Instructions

### 1. Database Setup
1. Open your MySQL client (e.g., MySQL Workbench, phpMyAdmin, or terminal).
2. Run the code from `database.sql` to create the `petpaglus_db` database, necessary tables (`pets`, `adopters`, `adoption`), and insert sample data.

### 2. Application Configuration
1. Open `app.py`.
2. Locate the `DB_CONFIG` dictionary near the top.
3. If your MySQL root user has a password or if you created a separate user, update the `'password'` and `'user'` fields accordingly.

### 3. Install Dependencies
You need Python installed. In your terminal/command prompt, run:
```bash
pip install flask mysql-connector-python
```

### 4. Run the App
In the directory containing `app.py`, run:
```bash
python app.py
```
Open a browser and navigate to `http://127.0.0.1:5000` to interact with PETPAGLUS!
