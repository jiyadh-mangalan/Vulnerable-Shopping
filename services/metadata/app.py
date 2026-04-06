from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
@app.route("/latest/")
def latest():
    return jsonify(
        {
            "instance-id": "i-fake1234567890lab",
            "local-ipv4": "10.0.0.42",
        }
    )


@app.route("/latest/meta-data/iam/security-credentials/lab-role")
def creds():
    return jsonify(
        {
            "Code": "Success",
            "AccessKeyId": "AKIAFAKE123456789LAB",
            "SecretAccessKey": "fakeSecretKeyForVulnLabOnly999",
            "Token": "fake-session-token",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
