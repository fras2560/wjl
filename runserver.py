import os
from app import wjl_app
if __name__ == "__main__":
    if (os.environ.get("DATABASE_URL") == "" or
            os.environ.get("DATABASE_URL") is None):
        from initDB import init_database
        print("Initializing database")
        init_database()
    
    start = False
    wjl_app.run(host='0.0.0.0', port=8080)
