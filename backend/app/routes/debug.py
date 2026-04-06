import os
import pickle

import requests
import yaml
from flask import current_app, jsonify, request

from app.routes import bp_debug

LOG_DIR = "/app/logs"


@bp_debug.route("/ssrf", methods=["GET", "POST"])
def ssrf_demo():
    # VULN-035: SSRF — no blocklist
    url = request.args.get("url") or (request.get_json() or {}).get("url")
    if not url:
        return jsonify({"error": "url required"}), 400
    try:
        r = requests.get(url, timeout=5)
        return jsonify(
            {"status": r.status_code, "body": r.text[:8000], "headers": dict(r.headers)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_debug.route("/lfi", methods=["GET"])
def lfi_demo():
    # VULN-036: path traversal / LFI — maps to lab-secrets
    name = request.args.get("file", "passwd")
    base = current_app.config.get("LAB_SECRETS_DIR", "/app/lab-secrets")
    path = os.path.normpath(os.path.join(base, name))
    if not path.startswith(os.path.normpath(base)):
        return jsonify({"error": "invalid"}), 400
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return jsonify({"path": path, "content": fh.read()})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@bp_debug.route("/lfi-raw", methods=["GET"])
def lfi_raw():
    # VULN-037: weaker — direct path fragment
    frag = request.args.get("path", "")
    path = "/app/lab-secrets/" + frag.replace("..", "")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return jsonify({"content": fh.read()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_debug.route("/import-pickle", methods=["POST"])
def import_pickle():
    # VULN-038: insecure deserialization
    raw = request.get_data()
    if not raw:
        return jsonify({"error": "empty"}), 400
    try:
        obj = pickle.loads(raw)
        return jsonify({"result": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp_debug.route("/import-yaml", methods=["POST"])
def import_yaml():
    # VULN-039: YAML unsafe load
    data = request.get_data()
    if not data:
        return jsonify({"error": "empty"}), 400
    try:
        obj = yaml.unsafe_load(data)
        return jsonify({"result": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp_debug.route("/error", methods=["GET"])
def verbose_error():
    # VULN-040: stack trace / verbose errors
    msg = request.args.get("msg", "boom")
    raise RuntimeError(msg)


@bp_debug.route("/secrets-leak", methods=["GET"])
def secrets_leak():
    # VULN-041: file path disclosure
    p = "/app/lab-secrets/api-keys.txt"
    try:
        with open(p) as fh:
            return jsonify({"file": p, "content": fh.read()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_debug.route("/poison-log", methods=["POST"])
def poison_log():
    # VULN-059: log poisoning — arbitrary line appended (PHP RCE chain analogue; here chains to SSTI)
    os.makedirs(LOG_DIR, exist_ok=True)
    data = request.get_json(silent=True) or {}
    line = data.get("msg") if isinstance(data, dict) else None
    if line is None:
        line = request.form.get("msg", "")
    path = os.path.join(LOG_DIR, "poison.log")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(str(line) + "\n")
    return jsonify({"ok": True, "path": path})


@bp_debug.route("/read-log", methods=["GET"])
def read_log_lfi():
    # VULN-060: LFI under /app/logs — read poisoned file before SSTI step
    name = request.args.get("file", "poison.log")
    path = os.path.normpath(os.path.join(LOG_DIR, name))
    if not path.startswith(os.path.normpath(LOG_DIR)):
        return jsonify({"error": "invalid"}), 400
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return jsonify({"path": path, "content": fh.read()})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@bp_debug.route("/ssti-from-log", methods=["GET"])
def ssti_from_log():
    # VULN-061: SSTI on full log file — chain: VULN-059 → VULN-061 (lab “RCE” via Jinja2)
    from jinja2 import Template

    name = request.args.get("file", "poison.log")
    path = os.path.normpath(os.path.join(LOG_DIR, name))
    if not path.startswith(os.path.normpath(LOG_DIR)):
        return jsonify({"error": "invalid"}), 400
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        return Template(content).render(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
