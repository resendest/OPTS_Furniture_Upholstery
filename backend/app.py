from flask import Flask
from backend.db import create_connection  # Import database connection functions

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Lousso Designs!"

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
