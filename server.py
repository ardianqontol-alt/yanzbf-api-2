from flask import Flask, request, jsonify
from garena import create_account

app = Flask(__name__)


@app.route("/api/yanzv1")
def yanzv1():
    try:
        count = int(request.args.get("count", 1))
        if count < 1 or count > 10:
            count = 1
    except ValueError:
        count = 1

    name = request.args.get("name", "YANZBF")
    region = request.args.get("region", "ID").upper()
    is_ghost = region == "GHOST"

    accounts = []
    for _ in range(count):
        try:
            acc = create_account(region=region, name_prefix=name, is_ghost=is_ghost)
            if acc:
                accounts.append(acc)
        except Exception:
            pass

    if not accounts:
        return jsonify({"success": False, "accounts": []})
    return jsonify({"success": True, "accounts": accounts})


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)