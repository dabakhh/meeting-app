# architecture du fichier database.py
# J'ai essayé cet exemple-ci plutôt que les variables d'environnements

import mysql.connector


def get_connection():
    
    connexion = mysql.connector.connect(
        host     = "localhost",     # "localhost" = MySQL tourne sur TON ordinateur
                                    # Si MySQL est sur un autre serveur tu mets son adresse IP
        user     = "root",          # ton nom d'utilisateur MySQL
                                    # sur WAMP/XAMPP c'est souvent "root" par défaut
        password = "mot_de_passe",              # ton mot de passe MySQL
                                    # sur WAMP c'est souvent vide par défaut
        database = "base_de_donnee",  # le nom de la base qu'on a créée à l'étape 1
                                
    )
    return connexion
    # On retourne la connexion pour pouvoir l'utiliser depuis app.py