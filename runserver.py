import os
from app import wjl_app
if __name__ == "__main__":
    start = False
    port = os.environ.get("WJL_PORT", 5000)
    while not start and port < 5010:
        try:
            wjl_app.run(debug=True, port=port)
            start = True
        except OSError as e:
            print(e)
            print(f"Port:{port} taken trying another")
            port += 1
