import subprocess
import ctypes
import os


import shutil

def charger_lib(chemin_lib, chemin_xmake):
    # 1) Tentative initiale
    if os.path.isfile(chemin_lib):
        try:
            lib = ctypes.CDLL(chemin_lib)
            print(f"[+] Librairie chargée : {chemin_lib}")
            return lib
        except OSError as e:
            print(f"[!] Impossible de charger la librairie : {e}")
            return None

    print(f"[!] La librairie '{chemin_lib}' est absente.")

    # 2) Vérifier si xmake est installé
    xmake_path = shutil.which("xmake")
    if not xmake_path:
        print("[!] xmake introuvable. Impossible de compiler la DLL.")
        return None

    print("[i] xmake trouvé. Compilation en cours...")

    # 3) Tenter de compiler le projet
    try:
        result = subprocess.run(
            [xmake_path],
            cwd=chemin_xmake,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        print("[+] Compilation réussie.")
    except subprocess.CalledProcessError as e:
        print("[!] Échec de la compilation avec xmake.")
        print(e.stdout)
        print(e.stderr)
        return None

    # 4) Recharger la DLL
    if os.path.isfile(chemin_lib):
        try:
            lib = ctypes.CDLL(chemin_lib)
            return lib
        except OSError as e:
            print(f"[!] Impossible de charger la librairie après compilation : {e}")
            return None
    else:
        print("[!] La DLL n'a pas été générée même après compilation.")
        return None