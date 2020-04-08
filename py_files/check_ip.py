from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=80, threaded=True)
