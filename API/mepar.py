# api/mepar.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        z = int(query.get('z', [0])[0])
        x = int(query.get('x', [0])[0])
        y = int(query.get('y', [0])[0])
        layer = query.get('layer', ['iier:topo10'])[0]

        # WMS BBOX matek (EPSG:3857)
        n = 2.0 ** z
        world_size = 40075016.68557849
        res = world_size / n
        minx = -20037508.342789244 + x * res
        maxy = 20037508.342789244 - y * res
        maxx = minx + res
        miny = maxy - res

        wms_url = (
            f"https://mepar.mvh.allamkincstar.gov.hu/api/proxy/iier-gs/wms?"
            f"SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS={layer}"
            f"&SRS=EPSG:3857&BBOX={minx},{miny},{maxx},{maxy}"
            f"&WIDTH=256&HEIGHT=256&FORMAT=image/png&TRANSPARENT=TRUE"
        )

        headers = {
            "Referer": "https://mepar.mvh.allamkincstar.gov.hu/",
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(wms_url, headers=headers)
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(r.content)
