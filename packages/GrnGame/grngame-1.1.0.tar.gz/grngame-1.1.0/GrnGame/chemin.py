
import os
import sys 
from .renvoielib import renvoie_lib


def retour_tout_chemin():
    libname = renvoie_lib()

    chemin_package = os.path.dirname(os.path.abspath(__file__)) 

    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
        chemin_lib = os.path.join(base_path, libname)
        chemin_script = base_path 
    else:

        chemin_lib = os.path.join(chemin_package, "dist", libname)
        if hasattr(sys, 'argv') and sys.argv:
            chemin_script = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            chemin_script = os.getcwd() 

    return chemin_package, chemin_script, chemin_lib