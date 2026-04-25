from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('classroom.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            student_id TEXT UNIQUE,
            name TEXT,
            email TEXT,
            department TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            capacity INTEGER,
            status TEXT DEFAULT 'available'
        )
    ''')
    
    # Insert demo data
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'faculty', 'faculty123', 'faculty')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (3, 'student', 'student123', 'student')")
    
    cursor.execute("INSERT OR IGNORE INTO classrooms VALUES (1, 'A101', 50, 'available')")
    cursor.execute("INSERT OR IGNORE INTO classrooms VALUES (2, 'A102', 40, 'occupied')")
    cursor.execute("INSERT OR IGNORE INTO classrooms VALUES (3, 'B201', 60, 'available')")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        conn = sqlite3.connect('classroom.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            return jsonify({'success': True, 'role': user[3]})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/dashboard/<role>')
def dashboard(role):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template(f'{role}/dashboard.html')

@app.route('/api/classrooms')
def get_classrooms():
    conn = sqlite3.connect('classroom.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classrooms")
    classrooms = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': c[0],
        'name': c[1],
        'capacity': c[2],
        'status': c[3],
        'current_class': 'Demo Class' if c[3] == 'occupied' else None
    } for c in classrooms])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message'].lower()
    
    if 'classroom' in message or 'room' in message:
        response = "A101 is available, A102 is occupied, B201 is available."
    elif 'attendance' in message:
        response = "Your attendance rate is 85%. You've attended 17 out of 20 classes."
    elif 'schedule' in message:
        response = "Today's classes: Data Structures at 9:00 AM in A101, Algorithms at 2:00 PM in B201."
    else:
        response = "I can help you with classroom availability, attendance records, and schedules. What would you like to know?"
    
    return jsonify({'response': response})

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    # Simulate face recognition
    return jsonify({'success': True, 'student_id': 1, 'message': 'Attendance marked successfully!'})

if __name__ == '__main__':
    init_db()
    print("🎓 Smart Classroom Management System Starting...")
    print("📍 Access the application at: http://localhost:5000")
    print("🔐 Login credentials:")
    print("   Admin: admin / admin123")
    print("   Faculty: faculty / faculty123") 
    print("   Student: student / student123")
    app.run(debug=True, host='0.0.0.0', port=5000)