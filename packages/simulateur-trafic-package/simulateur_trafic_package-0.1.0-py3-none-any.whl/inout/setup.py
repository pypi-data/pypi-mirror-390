from setuptools import setup
from Cython.Build import cythonize
import os

# Chemin absolu vers le fichier .pyx
pyx_file = os.path.join(os.path.dirname(__file__), "affichage_cython.pyx")

setup(
    name="affichage_cython_module",
    ext_modules=cythonize(
        pyx_file,
        compiler_directives={'language_level': "3"}
    ),
    zip_safe=False,
)
