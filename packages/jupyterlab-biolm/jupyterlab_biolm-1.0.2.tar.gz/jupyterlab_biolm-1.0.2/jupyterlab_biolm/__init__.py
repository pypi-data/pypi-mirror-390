"""
BioLM JupyterLab Extension
"""

def _jupyter_labextension_paths():
    """Called by Jupyter Lab Server to detect if it is a valid labextension and
    to install the widget

    Returns
    =======
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Lab copies from this directory during
        widget installation
    """
    return [{"src": "labextension", "dest": "jupyterlab-biolm"}]


def _jupyter_server_extension_points():
    """Return server extension points"""
    return [{
        'module': 'jupyterlab_biolm.serverextension',
    }]

