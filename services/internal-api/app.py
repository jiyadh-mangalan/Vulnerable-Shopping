from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
@app.route("/flag")
def flag():
    return jsonify(
        {
            "service": "internal-api",
            "flag": "VULN-LAB-INTERNAL-FLAG-001",
            "secret": "internal-only-not-for-internet",
        }
    )


@app.route("/latest/meta-data/iam/security-credentials/")
def meta():
    return jsonify({"Role": "fake-role"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
