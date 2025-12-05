from pile import Pile
from File import Files
from microbit import *
import radio

radio.on()
radio.config(channel=7)

class Arbitre:
    def __init__(self):
        self.dictio_joueurs = {} # {clé = "nom" valeur = "pile", ...}
        self.joueurs_c = 0  # Nombre de joueurs connectés
        self.nombre_manches = 0
        self.liste_symboles = ["pierre", "feuille", "ciseaux", "gorn", "spock"]

    def transition(self):
        """méthode qui crée une transition"""
        for y in range(5):
            for x in range(5):
                display.set_pixel(x, y, 9) 
                sleep(80)
        sleep(500)

    def connexion(self):
        """méthode qui attend la connexion des joueurs"""
        
        display.show(str(self.joueurs_c))
        while not button_a.is_pressed() :
            nom_joueur = radio.receive()  # reçoit un message
            sleep(50)

            # s'il n'y a pas de message on relance la boucle
            if not nom_joueur:  
                continue
            # on enlève les espaces pour éviter la création de faux-noms
            nom_joueur = nom_joueur.strip()  

            # si le nom est déjà dans la boucle il n'est pas accepté
            if nom_joueur not in self.dictio_joueurs :
                self.dictio_joueurs[nom_joueur] = Pile()
                self.joueurs_c = len(list(self.dictio_joueurs.keys()))
                display.show(str(self.joueurs_c))
                # on envoie "ok" à la carte joueur concerné
                radio.send(str("ok"))
                sleep(200)
        
        # On met une transition
        self.transition()
        sleep(1000)
        return

    def nombre_de_manche(self):
        """méthode qui permet de choisir le nombre de parties"""

        possibilite = "91357"
        f = Files()  # On crée une file f
        seuil_validation = 2000
        terminer = False
        for index in possibilite :
            f.enfiler(int(index))  # on enfile les chiffres de possibilite

        # permet d'afficher le nombre de manche
        manche = f.defiler()
        f.enfiler(manche)
        display.show(str(manche))

        # permet de faire défiler les nombres de parties
        # lorsqu'on appuie sur a les élément défile
        # lorsqu'on appuie sur b pendant 2sec les manches sont validés
        while not terminer:
            if button_a.was_pressed():
                manche = f.defiler()
                f.enfiler(manche)
                display.show(str(manche))
                sleep(200)
            if button_b.is_pressed():
                start = running_time()
                while button_b.is_pressed():
                    if running_time() - start > seuil_validation:
                        self.nombre_manches = manche
                        display.show(Image.YES)
                        sleep(300)
                        terminer = True
        
        # On met une transition
        self.transition()
        sleep(1000)
        return

    def lancer_manche(self):
        """méthode qui permet de lancer la manche"""

        # on envoie à vos choix aux joueurs
        radio.send("à vos choix")
        sleep(1000)
        compteur = 0  # compte le nombre de symbole reçu

        # on attend les choix de joueurs
        while compteur < self.joueurs_c :
            symbole = radio.receive()
            sleep(50)
            if not symbole:
                continue
            s = symbole.strip()  # on enlève les espaces inutiles
            if ":" not in s:
                continue
            nom, choix = s.split(":")
            ###################################
            # On vérifie en cas de réel problème
            if nom not in self.dictio_joueurs:
                continue
            if choix not in self.liste_symboles:
                continue
            ###################################

            # on empile le choix du joueur
            self.dictio_joueurs[nom].empiler(choix)
            compteur += 1
        return

    def vainqueur_manche(self):
        """méthode qui permet de définir le vainqueur de la manche"""

        regles = {"pierre": ["ciseaux", "gorn"],
                  "feuille": ["pierre", "spock"],
                  "ciseaux": ["feuille", "gorn"],
                  "gorn": ["feuille", "spock"],
                  "spock": ["pierre", "ciseaux"]}
        choix_joueurs = {}
        for nom, choix in self.dictio_joueurs.items():
            choix_joueurs[nom] = choix.depiler()
        score_manche = {nom: 0 for nom in self.dictio_joueurs.keys()}

        for joueur1, choix1 in choix_joueurs.items():
            for joueur2, choix2 in choix_joueurs.items():
                if joueur1 == joueur2:
                    continue
                    # permet de ne pas comparer le joueur1 avec lui même
                    # permet de passer au suivant
                if choix2 in regles[choix1]:
                    score_manche[joueur1] += 1

        # On met les points à la place des symboles retirés précédement
        # On calcule aussi le score max de la manche avec max_points
        max_points = 0
        for nom, points in score_manche.items():
            if points > max_points :
                max_points = points
            self.dictio_joueurs[nom].empiler(points)

        # On affiche le gagnant ou les gagnants ex aequo de la manche
        gagnants = [nom for nom, pts in score_manche.items() if pts == max_points]
        for gagnant in gagnants:
            radio.send(gagnant)
            sleep(200)
        return

    def vainqueur_partie(self):
        """méthode qui permet de définir le vainqueur de la partie"""

        score_fin_part = {nom: 0 for nom in self.dictio_joueurs.keys()}

        # on dépile tous les points de chaque joueur et on les additionne
        for nom, pile_points in self.dictio_joueurs.items():
            while not pile_points.est_vide():  # tant que la pile n'est pas vide
                score_fin_part[nom] += pile_points.depiler()

        # On calcule le score max de la partie avec max_points
        max_points = 0
        for nom, points in score_fin_part.items():
            if points > max_points :
                max_points = points

        # on identifie les gagnants
        gagnants = [nom for nom, score in score_fin_part.items() if score == max_points]
        for gagnant in gagnants:
            radio.send(gagnant)
            sleep(500)
        return
    
    def lancer_partie(self):
        """méthode principale"""

        # on lance la méthode :
        self.connexion()
        # on lance la méthode :
        self.nombre_de_manche()
        radio.send("go")
        sleep(200)
        for i in range(self.nombre_manches):
            display.show(str(i+1))
            sleep(1000)
            # on lance la méthode :
            self.lancer_manche()
            # on lance la méthode :
            self.vainqueur_manche()
            sleep(1000)
        # on envoie le message :
        radio.send("partie finie")
        sleep(1000)
        # on lance la méthode :
        self.vainqueur_partie()
        # on lance la méthode :
        self.transition()
        return

y = Arbitre()
print(y.lancer_partie())