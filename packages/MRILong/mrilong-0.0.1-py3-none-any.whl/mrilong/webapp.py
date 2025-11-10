from __future__ import annotations
import os
from typing import Optional


def launch_viewer_if_requested(x_sample, y_pred, y_gt=None, figs_dir: Optional[str] = None, open_browser: bool = False) -> Optional[str]:
    """Best-effort launch of the bundled web inference viewer.

    Looks for: LongitudinalAnalysisAIIMS.pypi/MEDNet/webview/WebInteractivePlotInference.py
    Returns URL string if launched, else None.
    """
    try:
        import importlib.util as _ilu
        viewer_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "MEDNet", "webview", "WebInteractivePlotInference.py")
        )
        if not os.path.exists(viewer_path):
            return None
        spec = _ilu.spec_from_file_location("webplot_infer", viewer_path)
        if not spec or not spec.loader:
            return None
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        url = mod.launch_web_inference_viewer(
            X_sample=x_sample,
            Y_pred=y_pred,
            Y_gt=y_gt,
            figs_dir=(figs_dir or "."),
            open_browser=open_browser,
            allow_save=True,
        )
        return url
    except Exception:
        return None
