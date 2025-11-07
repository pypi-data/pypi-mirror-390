
import subprocess
import ctypes


def installer_xmake(systeme):
    """Installe xmake selon l'OS."""
    try:
        if systeme == "linux" or systeme == "mac":
            # Tentative avec curl puis fallback wget
            try:
                subprocess.run(
                    ["bash", "-c", "curl -fsSL https://xmake.io/shget.text | bash"],
                    check=True
                )
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["bash", "-c", "wget https://xmake.io/shget.text -O - | bash"],
                    check=True
                )

        elif systeme == "windows":
            subprocess.run(
                ["powershell", "-Command", "irm https://xmake.io/psget.text | iex"],
                check=True
            )

        else:
            raise RuntimeError("Système non supporté pour installation auto de xmake.")

    except subprocess.CalledProcessError:
        raise RuntimeError("Échec de l'installation automatique de xmake.")


def charger_lib(chemin_lib, chemin_xmake, systeme):
    """
    chemin_lib  : chemin complet vers la librairie (.dll / .so / .dylib)
    chemin_xmake : dossier contenant le projet xmake
    systeme : string déjà fourni par renvoie_systeme()
    """

    # 1) Tentative initiale
    try:
        return ctypes.CDLL(chemin_lib)

    except OSError:
        print(f"[!] Impossible de charger : {chemin_lib}")
        print("[i] Vérification de xmake...")

        # 2) Vérifier si xmake est installé
        xmake_installe = (subprocess.run(["xmake", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0)

        if not xmake_installe:
            print("[!] xmake introuvable. Installation en cours...")
            installer_xmake(systeme)
            print("[+] xmake installé.")

        # 3) Compiler
        print("[i] Compilation du projet...")
        try:
            subprocess.run(
                ["xmake"],
                cwd=chemin_xmake,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("Échec de la compilation avec xmake.")

        print("[+] Compilation réussie. Rechargement de la librairie...")

        # 4) Rechargement
        try:
            return ctypes.CDLL(chemin_lib)
        except OSError:
            raise RuntimeError("Librairie introuvable même après compilation.")
