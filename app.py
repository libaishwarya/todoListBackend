from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity,decode_token
from flask_mysqldb import MySQL
import mysql.connector
import jwt
app = Flask(__name__)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="mydatabase"
)
    
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config["JWT_IDENTITY_CLAIM"] = "user_id"
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    mailID = data['mailID']
    passwords = data['passwords']
    cursor = mydb.cursor()
    sql = "INSERT INTO userDetails (name, mailID, passwords) VALUES (%s, %s, %s)"
    val = (name, mailID, passwords)
    cursor.execute(sql, val)
    mydb.commit()
    return jsonify({'message': 'User registered successfully.'})

@app.route('/login', methods=['POST'])
def login():
    name = request.json.get('name')
    passwords = request.json.get('passwords')
    cursor = mydb.cursor()
    # cursor.execute("SELECT id, name, passwords FROM userDetails WHERE name=%s, passwords=%s" (name,passwords))
    cursor.execute("SELECT id, name, passwords FROM userDetails WHERE name=%s AND passwords=%s", (name, passwords))

    user = cursor.fetchone()
    if user and passwords == user[2]:
        access_token = create_access_token(identity=user[0])
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Invalid username or password"}), 401
    
@app.route('/todo', methods =['POST'])
def addTodo():
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        if len(auth_header) == 0:
            return jsonify({"error" : "not authorized"}), 401
        token = auth_header.split()[1]
        token_data = decode_token(token)
        user_id = token_data["user_id"]
        json_data = request.get_json()
        todo_data = json_data["todo"]
        cursor =mydb.cursor()
        cursor.execute("insert into taskDetails (userID,todo) values (%s, \"%s\" )", (user_id,todo_data))
        mydb.commit()
        cursor.close()
        
        return "",201
    else:
        return jsonify({"error" : "not authorized"}), 401
    
@app.route('/listTodo', methods = ['GET'])
@jwt_required()
def getTodo():
    current_user = get_jwt_identity()
    cur = mydb.cursor()
    cur.execute("SELECT * FROM taskDetails WHERE userID=%s", (current_user,))
    todos = cur.fetchall()

    todo_list = []
    for row in todos:
        todo = {
            'id': row[0],
            'userID': row[1],
            'todo': row[2]
        }
        todo_list.append(todo)
    cur.close()
    return jsonify(todo_list)

if __name__ == '__main__':
    app.run(debug=True)
    