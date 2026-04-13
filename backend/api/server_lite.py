from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'lite_healthy'})

if __name__ == '__main__':
    print("🌟 Starting LITE Islamic AI Agent Web API...")
    app.run(debug=False, host='0.0.0.0', port=5001)
