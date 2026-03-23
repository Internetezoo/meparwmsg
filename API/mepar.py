from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/api/mepar', methods=['GET'])
def handler():
    # Paraméterek kinyerése a Locus kéréséből
    z = request.args.get('z', type=int)
    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)
    layer = request.args.get('layer', 'iier:topo10')

    # Ha GetCapabilities kérés érkezik (réteglista)
    if request.args.get('REQUEST') == 'GetCapabilities':
        wms_cap_url = "https://mepar.mvh.allamkincstar.gov.hu/api/proxy/iier-gs/wms?SERVICE=WMS&REQUEST=GetCapabilities"
        r = requests.get(wms_cap_url, headers={"Referer": "https://mepar.mvh.allamkincstar.gov.hu/"})
        return Response(r.content, mimetype='text/xml')

    # Alapértelmezett válasz, ha nincsenek koordináták
    if None in (z, x, y):
        return "MePAR Proxy aktív. Használat: ?z={z}&x={x}&y={y}", 200

    # WMS BBOX számítás (Web Mercator)
    n = 2.0 ** z
    world_size = 40075016.68557849
    res = world_size / n
    minx = -20037508.342789244 + x * res
    maxy = 20037508.342789244 - y * res
    maxx = minx + res
    miny = maxy - res

    # A tényleges MePAR WMS hívás
    target_url = (
        f"https://mepar.mvh.allamkincstar.gov.hu/api/proxy/iier-gs/wms?"
        f"SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS={layer}"
        f"&SRS=EPSG:3857&BBOX={minx},{miny},{maxx},{maxy}"
        f"&WIDTH=256&HEIGHT=256&FORMAT=image/png&TRANSPARENT=TRUE"
    )

    headers = {
        "Referer": "https://mepar.mvh.allamkincstar.gov.hu/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"
    }

    try:
        r = requests.get(target_url, headers=headers, timeout=20)
        return Response(r.content, mimetype='image/png')
    except Exception as e:
        return str(e), 500

# Ez a sor segít a Vercelnek felismerni a belépési pontot
app.debug = False
