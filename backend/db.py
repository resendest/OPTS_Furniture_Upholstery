import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# 1) Build path to .env in project root
env_path = Path(__file__).resolve().parent.parent / '.env'
print(f"Looking for .env at: {env_path}")

# 2) Does it exist?
print("→ .env exists?", env_path.exists())

# 3) (If it exists) print first few lines to confirm contents
if env_path.exists():
    print("→ .env content preview:")
    for i, line in enumerate(env_path.read_text().splitlines()):
        print(f"   {i+1}: {line}")
        if i >= 4: break  # only show first 5 lines

# 4) Load it
load_dotenv(dotenv_path=env_path)

# 5) Show what we loaded
print("MySQL ENV VALUES →", {
    "HOST":     os.getenv("DB_HOST"),
    "USER":     os.getenv("DB_USER"),
    "PASSWORD": "••••••" if os.getenv("DB_PASSWORD") else None,
    "DATABASE": os.getenv("DB_NAME"),
})

def create_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
        )
        print("✅ MySQL connection established.")
        return conn
    except mysql.connector.Error as e:
        print("❌ Error connecting to MySQL:", e)
        return None

