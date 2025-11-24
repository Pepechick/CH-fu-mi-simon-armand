from File import Files
from microbit import *
import radio

radio.on()
radio.config(channel=7)

class Joueur:
    def __init__(self):
        self.name = None        # Le choix du nom se fait en début de partie
        self.choix = None       # Le choix correspond à la valeur choisi à chaque manche
        self.connecte = "non"  # Oui quand le joueur à appuyé sur A pendant 5sec

    def Choix_du_nom(self):
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        f = Files()
        liste_nom = []
        seuil_validation = 2000
        terminer = False
        for index in alpha :
            f.enfiler(index)
        lettre = f.defiler()
        f.enfiler(lettre)
        display.show(str(lettre))

        while not terminer:
            if button_a.was_pressed():
                lettre = f.defiler()
                f.enfiler(lettre)
                display.show(str(lettre))
                sleep(200)
            if button_b.was_pressed():
                liste_nom.append(lettre)
                display.show(Image.YES)
                sleep(300)
                display.show(str(lettre))
            if button_b.is_pressed():
                t0 = running_time()
                while button_b.is_pressed():
                    if running_time() - t0 > seuil_validation:
                        terminer = True
                        break

        self.name = "".join(liste_nom)
        display.scroll(self.name)
        sleep(1000)
        return self.name

    def Choix_symbole(self):
        dictio_symboles = {"pierre" : Image('09990:''90009:''90009:''90009:''09990:'),
                           "feuille" : Image('99999:''90009:''90009:''90009:''99999:'),
                           "ciseaux" : Image('90009:''09090:''00900:''09090:''09090:'),
                           "gorn" : Image('99999:''00009:''99999:''90000:''99999:'),
                           "spock" : Image('09090:''09090:''09990:''99990:''09990:')}
        f = Files()
        seuil_validation = 2000
        terminer = False
        for cle, valeur in dictio_symboles.items():
            f.enfiler((cle, valeur))
        symbole_courant = f.defiler()
        if symbole_courant is not None:
            cle, image = symbole_courant
            f.enfiler(symbole_courant)
            display.show(image)

        while not terminer:
            if button_a.was_pressed():
                symbole_courant = f.defiler()
                if symbole_courant is not None:
                    cle, image = symbole_courant
                    f.enfiler(symbole_courant)
                    display.show(image)
                    sleep(200)
            if button_b.is_pressed():
                start = running_time()
                while button_b.is_pressed():
                    if running_time() - start > seuil_validation:
                        if symbole_courant is not None:
                            self.choix = symbole_courant[0]  # clé du symbole
                            display.show(Image.YES)
                            sleep(300)
                            terminer = True
                        break

        display.show(str(self.choix))
        sleep(1000)
        return self.choix

    def connexion(self):
        display.scroll("APPUI 3s")
        while self.connecte == "non":
            if button_a.is_pressed() or button_b.is_pressed():
                start = running_time()
                while button_a.is_pressed() or button_b.is_pressed():
                    if running_time() - start > 3000:
                        self.connecte = "oui"
                        display.show("C")  # Connected
                        sleep(500)
                        radio.send(str(self.name))  # envoyer le nom à la carte arbitre
                        break
        sleep(1000)
        return self.connecte
