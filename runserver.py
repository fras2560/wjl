import os
from app import wjl_app
if __name__ == "__main__":
    if (os.environ.get("DATABASE_URL") == "" or
            os.environ.get("DATABASE_URL") is None):
        from initDB import init_database
        print("Initializing database")
        init_database()
    start = False
    port = os.environ.get("WJL_PORT", 5000)
    debug = os.environ.get("DEBUG", False)
    while not start and port < 5010:
        try:
            wjl_app.run(debug=debug, port=port)
            start = True
        except OSError as e:
            print(e)
            print(f"Port:{port} taken trying another")
            port += 1
