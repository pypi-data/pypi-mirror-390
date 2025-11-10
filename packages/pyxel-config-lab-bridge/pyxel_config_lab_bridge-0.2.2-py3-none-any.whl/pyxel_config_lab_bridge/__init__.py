from IPython.display import HTML, display

__version__ = "0.2.1"


def open_pyxel_config_lab() -> None:
    """Display the Pyxel Config Lab UI directly inside the Jupyter notebook."""
    try:
        print(f"🧠 pyxel_config_lab_bridge version {__version__}")
        html = """
        <div style="border: 2px solid #3c3c3c; border-radius: 10px; overflow: hidden;">
            <iframe
                src="https://pyxel-config-lab-ede25c.gitlab.io/"
                width="100%"
                height="600"
                style="border: none;">
            </iframe>
        </div>
        """
        display(HTML(html))
        print("✅ Pyxel Config Lab loaded inside notebook.")
    except Exception as e:
        print(f"❌ Error displaying Pyxel Config Lab: {e}")


def _jupyter_labextension_paths():
    """Tell JupyterLab where to find the labextension assets."""
    return [{"src": "labextension", "dest": "pyxel-config-lab"}]
