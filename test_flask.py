from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello(): return "OK"
if __name__ == "__main__":
    print("Minimal Flask starting...")
    app.run(port=5002)
