from flask import Flask, request, jsonify
from backend.session_manager import SessionManager
from datetime import datetime

app = Flask(__name__)

@app.route('/api/global_high_score', methods=['GET'])
def global_high_score():
    mode = request.args.get('mode')
    category = request.args.get('category')
    session_manager = SessionManager()
    result = session_manager.get_global_high_score_current_month(mode, category)
    if result:
        return jsonify(result)
    else:
        return jsonify({'nickname': None, 'score': None, 'mode': mode, 'subject': category})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 