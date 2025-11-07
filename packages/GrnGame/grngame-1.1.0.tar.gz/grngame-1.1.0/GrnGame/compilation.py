import os
import sys 
import subprocess
def compilation_main(systeme, chemin_lib):
    import argparse
    
    # Parser les arguments
    parser = argparse.ArgumentParser(
        description="Compile un script Python en exécutable avec Grngame",
        usage="GrnGame_app script.py [--noconsole] [--icon chemin/vers/icone.ico]"
    )
    parser.add_argument("script", help="Fichier Python à compiler")
    parser.add_argument("--noconsole", action="store_true", 
                       help="Cache la console (Windows uniquement)")
    parser.add_argument("--icon", type=str, default=None,
                       help="Chemin vers l'icône (.ico pour Windows, .icns pour macOS)")
    
    args = parser.parse_args(sys.argv[1:])
    
    script_to_compile = args.script
    
    # Vérifier que le script existe
    if not os.path.exists(script_to_compile):
        print(f"Erreur : Le fichier '{script_to_compile}' n'existe pas.")
        return 1
    
    # Déterminer le séparateur selon le système
    if systeme == "windows":
        separator = ";"
    elif systeme in ["linux", "darwin"]:
        separator = ":"
    else:
        raise OSError(f"Système non pris en charge : {systeme}")
    
    # Construire la commande de base
    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        f"--add-binary={chemin_lib}{separator}."
    ]
    
    # Ajouter l'option noconsole si demandée (Windows uniquement)
    if args.noconsole:
        if systeme == "windows":
            cmd.append("--noconsole")
            print("Mode sans console activé")
        else:
            print("Avertissement : --noconsole est ignoré (uniquement Windows)")
    
    # Ajouter l'icône si spécifiée
    if args.icon:
        if os.path.exists(args.icon):
            cmd.append(f"--icon={args.icon}")
            print(f"Icône ajoutée : {args.icon}")
        else:
            print(f"Avertissement : L'icône '{args.icon}' n'existe pas, elle sera ignorée.")
    
    # Ajouter le script à compiler
    cmd.append(script_to_compile)
    
    # Afficher la commande
    print("\nCommande de compilation :")
    print(" ".join(cmd))
    print()
    
    # Exécuter la compilation
    try:
        subprocess.run(cmd, check=True,creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("\nCompilation terminée avec succès.")
        
        # Afficher le chemin de l'exécutable
        exe_name = os.path.splitext(os.path.basename(script_to_compile))[0]
        if systeme == "windows":
            exe_name += ".exe"
        exe_path = os.path.join("dist", exe_name)
        print(f"Exécutable créé : {os.path.abspath(exe_path)}")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\nÉchec de la compilation : {e}")
        return 1
    except FileNotFoundError:
        print("\nErreur : PyInstaller n'est pas installé.")
        print("Installez-le avec : pip install pyinstaller")
        return 1