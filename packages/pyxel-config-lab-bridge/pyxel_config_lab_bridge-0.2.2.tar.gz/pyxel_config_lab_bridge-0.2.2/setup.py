from setuptools import setup, find_packages

setup(
    name="pyxel-config-lab",
    version="0.2.0",
    description="JupyterLab panel embedding the Pyxel Config Lab UI",
    author="Doby Baxter",
    license="BSD-3-Clause",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["jupyterlab>=4.0"],
    entry_points={
        "jupyterlab.extension": [
            "pyxel-config-lab = pyxel_config_lab_bridge"
        ]
    },
)
