import io
import json
import os
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

# Use Agg backend (headless-safe)
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Inference – GT vs Prediction</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 16px; background:#111; color:#eee; }
    .controls { display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
    button { padding:6px 10px; border:none; border-radius:6px; cursor:pointer; background:#2E86AB; color:white; }
    button.secondary { background:#F18F01; }
    button.danger { background:#A23B72; }
    label { font-size:12px; color:#ccc; }
    input[type=number] { width:4rem; margin-left:4px; }
    .panel { display:flex; flex-direction:column; align-items:flex-start; gap:8px; }
    img { background:black; max-width:95vw; height:auto; border-radius:8px; }
    .meta { font-size:12px; color:#ccc; }
    .indices { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; color:#ddd; }
  </style>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-store" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
</head>
<body>
  <div class="controls">
    <button id="shuffle" class="danger">Shuffle Slices</button>
    <button id="reset" class="secondary">Reset</button>
    <button id="savefig">Save Figure</button>
    <label>Z <input id="zidx" type="number" value="0" min="0" step="1"></label>
    <label>Y <input id="yidx" type="number" value="0" min="0" step="1"></label>
    <label>X <input id="xidx" type="number" value="0" min="0" step="1"></label>
    <span id="savehint" class="meta"></span>
  </div>
  <div class="panel">
    <img id="grid" src="" alt="grid">
    <div id="meta" class="meta"></div>
    <div class="indices" id="indices"></div>
  </div>

<script>
let meta = null;
let z = 0, y = 0, x = 0;

function qs(sel){ return document.querySelector(sel); }
function clamp(v, lo, hi){ v = parseInt(v||0,10); return Math.max(lo, Math.min(hi, v)); }

async function loadMeta() {
  const r = await fetch('meta');
  meta = await r.json();
  z = meta.mid.z; y = meta.mid.y; x = meta.mid.x;
  qs('#zidx').max = meta.dims[0]-1; qs('#zidx').value = z;
  qs('#yidx').max = meta.dims[1]-1; qs('#yidx').value = y;
  qs('#xidx').max = meta.dims[2]-1; qs('#xidx').value = x;
  qs('#meta').innerText = `Dims: ${meta.dims.join(' x ')} | Classes: ${meta.classes.join(', ')}`;
  updateGrid();
}

function updateGrid(){
  const ts = Date.now();
  qs('#grid').src = `grid?z=${z}&y=${y}&x=${x}&_=${ts}`;
  qs('#indices').innerText = `Z=${z} | Y=${y} | X=${x}`;
}

qs('#zidx').addEventListener('change', () => { z = clamp(qs('#zidx').value, 0, meta.dims[0]-1); updateGrid(); });
qs('#yidx').addEventListener('change', () => { y = clamp(qs('#yidx').value, 0, meta.dims[1]-1); updateGrid(); });
qs('#xidx').addEventListener('change', () => { x = clamp(qs('#xidx').value, 0, meta.dims[2]-1); updateGrid(); });

qs('#shuffle').addEventListener('click', async () => {
  try {
    const r = await fetch(`rand_indices?z=${z}&y=${y}&x=${x}&_=${Date.now()}`, {cache:'no-store'});
    const res = await r.json();
    z = res.z; y = res.y; x = res.x;
    qs('#zidx').value = z; qs('#yidx').value = y; qs('#xidx').value = x;
    updateGrid();
  } catch(e){ console.error(e); }
});

qs('#reset').addEventListener('click', () => {
  z = meta.mid.z; y = meta.mid.y; x = meta.mid.x;
  qs('#zidx').value = z; qs('#yidx').value = y; qs('#xidx').value = x;
  updateGrid();
});

qs('#savefig').addEventListener('click', async () => {
  const r = await fetch(`save_grid?z=${z}&y=${y}&x=${x}`, {cache:'no-store'});
  const res = await r.json();
  qs('#savehint').innerText = res.path ? `Saved: ${res.path}` : (res.error || 'Save failed');
});

loadMeta();
</script>
</body>
</html>
"""


def _safe_bounds(n: int) -> tuple[int, int]:
    if n <= 10:
        return 0, n
    lo, hi = 5, n - 5
    if hi <= lo:
        return 0, n
    return lo, hi


def _rgba_overlay(mask2d: np.ndarray) -> np.ndarray:
    h, w = mask2d.shape
    out = np.zeros((h, w, 4), dtype=np.float32)
    out[mask2d == 1] = [1.0, 0.0, 0.0, 0.55]
    out[mask2d == 2] = [0.0, 1.0, 0.0, 0.55]
    out[mask2d == 3] = [0.0, 0.0, 1.0, 0.55]
    return out


def _figure_pair_grid(X: np.ndarray, Ygt: np.ndarray, Ypr: np.ndarray, z: int, y: int, x: int) -> bytes:
    fig = Figure(figsize=(12, 7), dpi=110)
    axs = fig.subplots(2, 3)
    # Normalize indices
    Dz, Dy, Dx = X.shape
    z = max(0, min(Dz - 1, int(z)))
    y = max(0, min(Dy - 1, int(y)))
    x = max(0, min(Dx - 1, int(x)))

    planes = [
        ('Axial (Z)', X[z, :, :], Ygt[z, :, :], Ypr[z, :, :], z),
        ('Coronal (Y)', X[:, y, :], Ygt[:, y, :], Ypr[:, y, :], y),
        ('Sagittal (X)', X[:, :, x], Ygt[:, :, x], Ypr[:, :, x], x),
    ]

    for c, (title, x2d, gt2d, pr2d, idx) in enumerate(planes):
        vmin, vmax = np.percentile(x2d, [5, 95]).astype(float)
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
            vmin, vmax = float(np.min(x2d)), float(np.max(x2d) if np.max(x2d) != np.min(x2d) else np.min(x2d) + 1.0)
        # Row 0: GT
        ax = axs[0, c]; ax.axis('off')
        ax.imshow(x2d, cmap='gray', vmin=vmin, vmax=vmax, interpolation='nearest')
        ax.imshow(_rgba_overlay(gt2d), interpolation='nearest')
        ax.set_title(f"{title} – GT (slice {idx})", fontsize=9)
        # Row 1: Pred
        ax = axs[1, c]; ax.axis('off')
        ax.imshow(x2d, cmap='gray', vmin=vmin, vmax=vmax, interpolation='nearest')
        ax.imshow(_rgba_overlay(pr2d), interpolation='nearest')
        ax.set_title(f"{title} – Pred", fontsize=9)

    fig.tight_layout(pad=0.5)
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    return buf.getvalue()


class _Handler(BaseHTTPRequestHandler):
    X = None
    Ygt = None
    Ypr = None
    figs_dir = None
    ALLOW_SAVE = True

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, ctype="text/html; charset=utf-8", body=b"", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.lstrip("/")
        q = urllib.parse.parse_qs(parsed.query)

        if path in ("", "index.html"):
            return self._send(200, body=_HTML.encode('utf-8'))

        if path == 'meta':
            Dz, Dy, Dx = self.X.shape
            mid = {
                'z': Dz // 2,
                'y': Dy // 2,
                'x': Dx // 2,
            }
            return self._send(200, 'application/json', json.dumps({
                'dims': [Dz, Dy, Dx],
                'classes': ['Background', 'CSF', 'Gray Matter', 'White Matter'],
                'mid': mid,
            }).encode('utf-8'))

        if path == 'grid':
            Dz, Dy, Dx = self.X.shape
            try:
                z = int(q.get('z', [Dz//2])[0]); y = int(q.get('y', [Dy//2])[0]); x = int(q.get('x', [Dx//2])[0])
            except Exception:
                z, y, x = Dz//2, Dy//2, Dx//2
            try:
                png = _figure_pair_grid(self.X, self.Ygt, self.Ypr, z, y, x)
                return self._send(200, 'image/png', png)
            except Exception as e:
                return self._send(500, 'application/json', json.dumps({'error': str(e)}).encode('utf-8'))

        if path == 'rand_indices':
            Dz, Dy, Dx = self.X.shape
            def rand_idx(n, cur):
                lo, hi = _safe_bounds(n)
                if hi <= lo:
                    return max(0, min(n-1, (cur+1) % max(1, n)))
                import random as _r
                tries = 0
                while True:
                    v = _r.randint(lo, max(lo, hi-1))
                    if v != cur or tries > 8:
                        return v
                    tries += 1
            try:
                cz = int(q.get('z', [Dz//2])[0]); cy = int(q.get('y', [Dy//2])[0]); cx = int(q.get('x', [Dx//2])[0])
            except Exception:
                cz, cy, cx = Dz//2, Dy//2, Dx//2
            payload = {'z': rand_idx(Dz, cz), 'y': rand_idx(Dy, cy), 'x': rand_idx(Dx, cx)}
            return self._send(200, 'application/json', json.dumps(payload).encode('utf-8'))

        if path == 'save_grid':
            if not getattr(self, 'ALLOW_SAVE', True):
                return self._send(403, 'application/json', json.dumps({'error': 'Save disabled'}).encode('utf-8'))
            Dz, Dy, Dx = self.X.shape
            try:
                z = int(q.get('z', [Dz//2])[0]); y = int(q.get('y', [Dy//2])[0]); x = int(q.get('x', [Dx//2])[0])
            except Exception:
                z, y, x = Dz//2, Dy//2, Dx//2
            try:
                png = _figure_pair_grid(self.X, self.Ygt, self.Ypr, z, y, x)
                os.makedirs(self.figs_dir, exist_ok=True)
                path = os.path.join(self.figs_dir, 'webview_infer_grid.png')
                with open(path, 'wb') as f:
                    f.write(png)
                return self._send(200, 'application/json', json.dumps({'path': path}).encode('utf-8'))
            except Exception as e:
                return self._send(500, 'application/json', json.dumps({'error': str(e)}).encode('utf-8'))

        return self._send(404, body=b'Not Found')


def launch_web_inference_viewer(X_sample: np.ndarray,
                                Y_pred: np.ndarray,
                                Y_gt: np.ndarray,
                                figs_dir: str | None = None,
                                host: str = '127.0.0.1',
                                port: int = 0,
                                open_browser: bool = True,
                                allow_save: bool = True) -> str:
    X = np.asarray(X_sample)
    Yp = np.asarray(Y_pred)
    Yg = np.asarray(Y_gt)
    if X.ndim != 3:
        raise ValueError(f"X must be 3D [D,H,W], got {X.shape}")
    if Yp.shape != X.shape or Yg.shape != X.shape:
        raise ValueError("Y_pred and Y_gt must match X shape")
    if figs_dir is None:
        figs_dir = os.path.join(os.path.dirname(__file__), 'saved.ckpt', 'Figs')

    handler = type('_InferHandler', (_Handler,), {})
    handler.X = X
    handler.Ygt = Yg
    handler.Ypr = Yp
    handler.figs_dir = figs_dir
    handler.ALLOW_SAVE = bool(allow_save)

    httpd = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{httpd.server_port}/"
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    print(f"Inference viewer at {url}")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    return url

