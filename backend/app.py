from flask import Flask
from db import create_connection, close_connection

app = Flask(__name__)

@app.route('/')
def home():
    connection = create_connection()
    if connection:
        close_connection(connection)
        return "Database connection test successful!"
    else:
        return "Failed to connect to the database."

@app.route('/get-data')
def get_data():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM your_table")
    data = cursor.fetchall()
    connection.close()
    return {"data": data}  # Returning the data as JSON

if __name__ == '__main__':
    app.run(debug=True)
