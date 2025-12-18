from app import create_app
from app.config import Config

app = create_app(Config)

if __name__ == "__main__":
    print("Starting Flask on http://127.0.0.1:5000 ...")
    app.run(debug=True)
