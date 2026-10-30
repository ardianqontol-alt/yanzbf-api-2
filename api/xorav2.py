import json
import sys
import os
import traceback
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

# Daftarkan folder root ke sys.path biar bisa import dari lib/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.garena import create_account


class handler(BaseHTTPRequestHandler):
    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)

            count = int(qs.get("count", ["1"])[0])
            name_prefix = qs.get("name", ["YANZBF"])[0]
            region = qs.get("region", ["ID"])[0].upper()

            if count < 1 or count > 10:
                count = 1

            is_ghost = region == "GHOST"

            accounts = []
            for _ in range(count):
                try:
                    acc = create_account(region=region, name_prefix=name_prefix, is_ghost=is_ghost)
                    if acc:
                        accounts.append(acc)
                except Exception:
                    pass

            if not accounts:
                return self._json(200, {"success": False, "accounts": []})

            return self._json(200, {"success": True, "accounts": accounts})

        except Exception as e:
            traceback.print_exc()
            return self._json(500, {"success": False, "error": str(e), "accounts": []})