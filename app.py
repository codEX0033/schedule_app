from flask import Flask, request, jsonify, make_response, render_template, send_from_directory, send_file, redirect
from flask_cors import CORS  
import pandas as pd
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  

UPLOAD_FOLDER = 'schedules'
ALLOWED_EXTENSIONS = {'xlsx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_schedule(class_name, day):
    path = os.path.join(UPLOAD_FOLDER, f"{day}.xlsx")
    if not os.path.exists(path):
        return []
    
    df = pd.read_excel(path, header=None)  
    
    schedule = []
    
    class_row = 1 
    class_col = None
    
    for col in range(3, len(df.columns)): 
        if str(df.iloc[class_row, col]) == class_name:
            class_col = col
            break
    
    if class_col is None:
        return []
    
    for row in range(2, len(df)):
        lesson_number = df.iloc[row, 1]
        if pd.isna(lesson_number):
            continue
            
        time = df.iloc[row, 2]
        lesson_info = df.iloc[row, class_col]
        
        classroom = df.iloc[row + 1, class_col]

        if pd.isna(lesson_info):
            continue
            
        if pd.isna(classroom):
            classroom = ""
        temp = []
        temp.append(int(lesson_number))
        temp.append(time)
        temp.append(lesson_info)
        temp.append(classroom)
        schedule.append(temp)

    return [list(map(lambda x: x.encode('utf-8').decode('utf-8') if isinstance(x, str) else x, item)) for item in schedule]

@app.route('/')
def index():
    if request.headers.get('Sec-Fetch-Mode') == 'navigate' and \
       request.headers.get('Sec-Fetch-Dest') == 'document' and \
       request.headers.get('Sec-Fetch-Site') == 'none':
        return redirect('/register')
    return send_from_directory('.', 'install.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/v1/get_schedule', methods=['GET'])
def get_schedule_api():
    class_name = request.args.get('class')
    day = request.args.get('day')
    
    if class_name and day:
        schedule = get_schedule(class_name, day)
        response = make_response(jsonify(schedule), 200)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    else:
        response = make_response(jsonify({"error": "Class and day parameters are required"}), 400)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

def init_database():
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_key TEXT NOT NULL,
            fio TEXT NOT NULL,
            class TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            status INTEGER NOT NULL DEFAULT 0
        )
        ''')
        
        cursor.execute('SELECT * FROM Users WHERE login = ?', ('sosal',))
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            cursor.execute('INSERT INTO Users (org_key, fio, class, login, password, status) VALUES (?, ?, ?, ?, ?, ?)', 
                          ('0000000000', 'admin', 'admin', 'sosal', 'admin-ne-sosot-adminy-sosyt', 1))
        
        connection.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        connection.close()

init_database()

@app.route('/api/main/initdb', methods=['GET'])
def initdb():
    key = request.args.get('key')

    if key == '1234567890':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        cursor.execute('DROP TABLE IF EXISTS Users')
        
        cursor.execute('''
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_key TEXT NOT NULL,
            fio TEXT NOT NULL,
            class TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            status INTEGER NOT NULL DEFAULT 0
        )
        ''')
        
        connection.commit()
        connection.close()
        return make_response(jsonify({"message": "Database initialized! Table Users created"}), 200)
    else:
        return make_response(jsonify({"error": "Invalid key"}), 401)

@app.route('/api/main/initadmin', methods=['GET'])
def initadmin():
    key = request.args.get('key')

    if key == '1234567890':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Users (org_key, fio, class, login, password, status) VALUES (?, ?, ?, ?, ?, ?)', 
                      ('0000000000', 'admin', 'admin', 'sosal', 'admin-ne-sosot-adminy-sosyt', 1))
        connection.commit()
        connection.close()
        return make_response(jsonify({"message": "admin created"}), 200)
    else:
        return make_response(jsonify({"error": "Invalid key"}), 401)

@app.route('/api/v1/login', methods=['POST'])
def login():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        cursor.execute('SELECT * FROM Users WHERE login = ? AND password = ? AND status = 1', (username, password))
        user = cursor.fetchone()

        if user:
            return make_response(jsonify({"message": "Login successful"}), 200)
        else:
            return make_response(jsonify({"error": "Неверный логин или пароль, или ваша заявка еще не подтверждена"}), 401)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        connection.close()

@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.get_json()
    
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute('INSERT INTO Users (org_key, fio, class, login, password, status) VALUES (?, ?, ?, ?, ?, ?)',
                      (data['org_key'], data['fio'], data['class'], data['login'], data['password'], 0))
        connection.commit()
        return make_response(jsonify({"message": "Registration request submitted successfully"}), 200)
    except sqlite3.IntegrityError:
        return make_response(jsonify({"error": "User already exists"}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        connection.close()

@app.route('/login')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/api/v1/admin/requests', methods=['GET'])
def get_requests():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT id, org_key, fio, class, login FROM Users WHERE status = 0')
        requests = cursor.fetchall()
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': req[0],
                'org_key': req[1],
                'fio': req[2],
                'class': req[3],
                'login': req[4]
            })
        
        return jsonify(requests_list)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        connection.close()

@app.route('/api/v1/admin/handle_request', methods=['POST'])
def handle_request():
    data = request.get_json()
    request_id = data.get('request_id')
    approve = data.get('approve')
    
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    try:
        if approve:
            cursor.execute('UPDATE Users SET status = 1 WHERE id = ?', (request_id,))
        else:
            cursor.execute('DELETE FROM Users WHERE id = ?', (request_id,))
            
        connection.commit()
        return jsonify({"message": "Request handled successfully"})
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        connection.close()

@app.route('/api/v1/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin_password = "admin-ne-sosot-adminy-sosyt"  

    if username == 'sosal' and password == admin_password:
        return make_response(jsonify({"message": "Login successful"}), 200)
    else:
        return make_response(jsonify({"error": "Invalid admin credentials"}), 401)

@app.route('/api/v1/admin/upload_schedule', methods=['POST'])
def upload_schedule():
    if 'file' not in request.files:
        return make_response(jsonify({"error": "No file part"}), 400)
    
    file = request.files['file']
    day = request.form.get('day')
    
    if not day:
        return make_response(jsonify({"error": "Day is required"}), 400)
    
    if file.filename == '':
        return make_response(jsonify({"error": "No selected file"}), 400)
    
    if file and allowed_file(file.filename):
        filename = f"{day}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            return make_response(jsonify({"message": "Schedule uploaded successfully"}), 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    return make_response(jsonify({"error": "Invalid file type"}), 400)

@app.route('/register')
def register_page():
    if request.headers.get('Sec-Fetch-Mode') == 'navigate' and \
       request.headers.get('Sec-Fetch-Dest') == 'document' and \
       request.headers.get('Sec-Fetch-Site') == 'none':
        return send_from_directory('.', 'register.html')
    return send_from_directory('.', 'install.html')

@app.route('/install')
def install_page():
    if request.headers.get('Sec-Fetch-Mode') == 'navigate' and \
       request.headers.get('Sec-Fetch-Dest') == 'document' and \
       request.headers.get('Sec-Fetch-Site') == 'none':
        return redirect('/register')
    return send_from_directory('.', 'install.html')

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json')

@app.route('/icon-192.png')
def icon_192():
    return send_file('icon-192.png')

@app.route('/icon-512.png')
def icon_512():
    return send_file('icon-512.png')

@app.after_request
def add_pwa_headers(response):
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory(APP_ROOT, 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)