
import os
from .chemin import retour_tout_chemin
from .systeme import renvoie_systeme
from .chargerlib import charger_lib
from .structures import *
from .signatures import configurer_signatures
from .compilation import compilation_main
chemin_package, chemin_script, chemin_lib = retour_tout_chemin()
import sys

def compilation():
    compilation_main(renvoie_systeme(),chemin_lib)

called_program = os.path.basename(sys.argv[0])
COMMANDES_INTERDITES = {"GrnGame_app", "GrnGame_xmake","GrnGame_app.exe", "GrnGame_xmake.exe"}


jeu = None
if called_program not in COMMANDES_INTERDITES:
    try:
        jeu = charger_lib(chemin_lib, os.path.join(chemin_package, "xmake"))
        if jeu is not None:
            configurer_signatures(jeu)
        else:
            print("[!] La lib n'a pas pu être chargée, le moteur est désactivé.")
    except Exception:
        print("[!] Erreur lors du chargement de la lib, le moteur est désactivé.")

        




if jeu is not None and called_program not in COMMANDES_INTERDITES:
    __all__ = [
        'jeu', 
        'GrnGame',
        'Gestionnaire', 
        'GestionnaireEntrees', 
        'FondActualiser', 
        'UpdateCallbackType', 
        'TAILLE_LIEN_GT', 
        'TAILLE_CANAL'
    ]
    class _grngame:
        def __init__(self):
            self._g = None
            self._callback_ref = None
            self._user_update = None

        def _get_absolute_path(self, relative_path):
            global chemin_script
            if os.path.isabs(relative_path):
                return relative_path
            else:
                return os.path.join(chemin_script, relative_path)

        def init(self, largeur=160, hauteur=90, fps=60, coeff=3,
                chemin_image=".", chemin_son=".",
                dessiner=True, bande_noir=True, r=0, g=0, b=0,
                update_func=None, nom_fenetre="fenetre",chemin_erreur ="erreurs.log"):
            chemin_erreur_abs = self._get_absolute_path(chemin_erreur)
            chemin_image_abs = self._get_absolute_path(chemin_image)
            chemin_son_abs = self._get_absolute_path(chemin_son)

            self._g = jeu.initialisation(
                hauteur, largeur, fps, coeff,
                chemin_image_abs.encode("utf-8"), chemin_son_abs.encode("utf-8"),
                dessiner, bande_noir, r, g, b, nom_fenetre.encode("utf-8"),chemin_erreur_abs.encode("utf-8")
            )
            if not self._g:
                raise RuntimeError("Initialisation échouée")

            if update_func:
                if not callable(update_func):
                    raise ValueError("update_func doit être callable")
                self._user_update = update_func

                def wrapper(g):
                    if self._user_update:
                        self._user_update()
                
                self._callback_ref = UpdateCallbackType(wrapper)
                jeu.set_update_callback(self._callback_ref)

            jeu.boucle_principale(self._g)

        @property
        def largeur(self):
            return self._g.contents.largeur if self._g else 0
        
        @property
        def hauteur(self):
            return self._g.contents.hauteur if self._g else 0
        
        @property
        def dt(self):
            return self._g.contents.dt if self._g else 0.0
        
        @property
        def fps(self):
            return self._g.contents.fps if self._g else 0.0
        
        @property
        def time(self):
            return self._g.contents.temps_frame if self._g else 0
        
        @property
        def mouse_x(self):
            return self._g.contents.entrees.contents.mouse_x if self._g else 0
        
        @property
        def mouse_y(self):
            return self._g.contents.entrees.contents.mouse_y if self._g else 0
        
        @property
        def mouse_presse(self):
            return self._g.contents.entrees.contents.mouse_pressed if self._g else False
        
        @property
        def mouse_juste_presse(self):
            return self._g.contents.entrees.contents.mouse_just_pressed if self._g else False
        
        @property
        def mouse_droit_presse(self):
            return self._g.contents.entrees.contents.mouse_right_pressed if self._g else False
        
        @property
        def mouse_droit_juste_presse(self):
            return self._g.contents.entrees.contents.mouse_right_just_pressed if self._g else False
        
        @property
        def decalage_x(self):
            if not self._g:
                return 0
            return self._g.contents.decalage_x / (
                self._g.contents.largeur_actuel / self._g.contents.largeur
            )
        
        @property
        def decalage_y(self):
            if not self._g:
                return 0
            return self._g.contents.decalage_y / (
                self._g.contents.hauteur_actuel / self._g.contents.hauteur
            )
        
        @property
        def run(self):
            return self._g.contents.run if self._g else False

        def touche_juste_presser(self, key_name):
            if not self._g:
                return False
            return jeu.touche_juste_presse(self._g, key_name.encode("utf-8"))

        def touche_enfoncee(self, key_name):
            if not self._g:
                return False
            return jeu.touche_enfoncee(self._g, key_name.encode("utf-8"))

        def touche_mannette_enfoncee(self, key_name):
            if not self._g:
                return False
            return jeu.touche_mannette_enfoncee(self._g, key_name.encode("utf-8"))

        def touche_mannette_juste_presse(self, key_name):
            if not self._g:
                return False
            return jeu.touche_mannette_juste_presse(self._g, key_name.encode("utf-8"))

        def dessiner_image(self, lien, x, y, w, h, sens=0, rotation=0):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            return jeu.ajouter_image_au_tableau(
                self._g, lien_abs.encode("utf-8"), x, y, w, h, sens, rotation
            )

        def dessiner_image_batch(self, ids, xs, ys, ws, hs, sens=None, rotations=None):
            if not self._g:
                return
            
            taille = len(ids)
            if sens is None:
                sens = [0] * taille
            if rotations is None:
                rotations = [0] * taille

            ids_abs = [self._get_absolute_path(s) for s in ids]

            ids_c = (c_char_p * taille)(*(s.encode("utf-8") for s in ids_abs))
            xs_c = (c_float * taille)(*xs)
            ys_c = (c_float * taille)(*ys)
            ws_c = (c_float * taille)(*ws)
            hs_c = (c_float * taille)(*hs)
            sens_c = (c_int * taille)(*sens)
            rotations_c = (c_int * taille)(*rotations)

            jeu.ajouter_image_au_tableau_batch(
                self._g, ids_c, xs_c, ys_c, ws_c, hs_c,
                sens_c, rotations_c, c_int(taille)
            )

        def dessiner_mot(self, lien, mot, x, y, coeff, ecart, sens=0, rotation=0):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            return jeu.ajouter_mot_dans_tableau(
                self._g, lien_abs.encode("utf-8"), mot.encode("utf-8"),
                x, y, coeff, sens, ecart, rotation
            )

        def jouer_son(self, lien, boucle=0, canal=-1):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            jeu.jouer_son(self._g, lien_abs.encode("utf-8"), boucle, canal)

        def arreter_son(self, lien):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            jeu.arreter_son(self._g, lien_abs.encode("utf-8"))

        def arreter_canal(self, canal):
            jeu.arreter_canal(canal)

        def pause_canal(self, canal):
            jeu.pause_canal(canal)

        def pause_son(self, lien):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            jeu.pause_son(self._g, lien_abs.encode("utf-8"))

        def reprendre_canal(self, canal):
            jeu.reprendre_canal(canal)

        def reprendre_son(self, lien):
            if not self._g:
                return
            lien_abs = self._get_absolute_path(lien)
            jeu.reprendre_son(self._g, lien_abs.encode("utf-8"))

        def init_mannette(self, index=0):
            if not self._g:
                raise RuntimeError("Jeu non initialisé")
            return jeu.init_controller_joysticks(self._g, index)

        def renvoie_joysticks(self, dead_zone=0.1):
            if not self._g:
                raise RuntimeError("Jeu non initialisé")
            entrees_ptr = self._g.contents.entrees
            if not entrees_ptr:
                return None

            ptr = jeu.renvoie_joysticks(entrees_ptr, dead_zone)
            if not ptr:
                return None
            return [ptr[i] for i in range(6)]

        def fermer_controller(self):
            if not self._g:
                return
            jeu.fermer_controller(self._g)

        def fermer_joystick(self):
            if not self._g:
                return
            jeu.fermer_joystick(self._g)

        def abs_val(self, x):
            return jeu.abs_val(c_double(x))
        
        def clamp(self, x, min_, max_):
            return jeu.clamp(c_double(x), c_double(min_), c_double(max_))
        
        def pow(self, base, exp):
            return jeu.pow_custom(c_double(base), c_double(exp))
        
        def sqrt(self, x):
            return jeu.sqrt_custom(c_double(x))
        
        def cbrt(self, x):
            return jeu.cbrt_custom(c_double(x))
        
        def exp(self, x):
            return jeu.exp_custom(c_double(x))
        
        def log(self, x):
            return jeu.log_custom(c_double(x))
        
        def log10(self, x):
            return jeu.log10_custom(c_double(x))
        
        def log2(self, x):
            return jeu.log2_custom(c_double(x))
        
        def sin(self, x):
            return jeu.sin_custom(c_double(x))
        
        def cos(self, x):
            return jeu.cos_custom(c_double(x))
        
        def tan(self, x):
            return jeu.tan_custom(c_double(x))
        
        def asin(self, x):
            return jeu.asin_custom(c_double(x))
        
        def acos(self, x):
            return jeu.acos_custom(c_double(x))
        
        def atan(self, x):
            return jeu.atan_custom(c_double(x))
        
        def atan2(self, y, x):
            return jeu.atan2_custom(c_double(y), c_double(x))
        
        def sinh(self, x):
            return jeu.sinh_custom(c_double(x))
        
        def cosh(self, x):
            return jeu.cosh_custom(c_double(x))
        
        def tanh(self, x):
            return jeu.tanh_custom(c_double(x))
        
        def asinh(self, x):
            return jeu.asinh_custom(c_double(x))
        
        def acosh(self, x):
            return jeu.acosh_custom(c_double(x))
        
        def atanh(self, x):
            return jeu.atanh_custom(c_double(x))
        
        def floor(self, x):
            return jeu.floor_custom(c_double(x))
        
        def ceil(self, x):
            return jeu.ceil_custom(c_double(x))
        
        def round(self, x):
            return jeu.round_custom(c_double(x))
        
        def trunc(self, x):
            return jeu.trunc_custom(c_double(x))
        
        def fmod(self, x, y):
            return jeu.fmod_custom(c_double(x), c_double(y))
        
        def hypot(self, x, y):
            return jeu.hypot_custom(c_double(x), c_double(y))

        def random(self, min_val, max_val):
            return jeu.random_jeu(min_val, max_val)

        def colorier(self, r, g, b):
            if not self._g:
                return
            return jeu.colorier(self._g, r, g, b)

        def redimensionner_fenetre(self):
            if not self._g:
                raise RuntimeError("Jeu non initialisé")
            jeu.redimensionner_fenetre(self._g)

        def ecrire_console(self, mot):
            return jeu.ecrire_dans_console(mot.encode("utf-8"))

        def stopper_jeu(self):
            if self._g:
                self._g.contents.run = False


        def set_update_callback(self, py_func):
            if not callable(py_func):
                raise ValueError("update doit être une fonction")
            self._user_update = py_func

        def update(self):
            if not self._g:
                raise RuntimeError("Jeu non initialisé")
            jeu.update(self._g)
            if self._user_update:
                self._user_update()


    GrnGame = _grngame()