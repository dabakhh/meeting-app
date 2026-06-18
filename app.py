# app.py 

from flask import Flask, render_template, redirect, url_for, request
# render_template = la fonction qui fusionne un fichier HTML avec des données
from database import get_connection
from datetime import datetime
# validation côté serveur - Champs Date et Heure
app = Flask(__name__)

@app.route("/")
def accueil():

    # ──────────────────────────────────────────────
    # ÉTAPE A : Ouvrir la connexion à MySQL
    # ──────────────────────────────────────────────
    conn = get_connection()
    # conn c'est notre "ligne téléphonique" ouverte avec MySQL

    cursor = conn.cursor(dictionary=True)
    # cursor c'est l'outil qui exécute les requêtes SQL
    # dictionary=True est TRÈS important :
    #   Sans : chaque livre = (1, 'Le Petit Prince', 'Saint-Exupéry', 1943, 1)
    #   Avec : {'contenu': '...', 'nom': 'Bensaid', 'prenom': 'Fatima', 'fonction': 'Présidente', ...}
    #
    # Avec dictionary=True on accède aux données par nom de colonne : reunion['titre']
    # C'est beaucoup plus lisible que reunion[1]

    # ──────────────────────────────────────────────
    # ÉTAPE B : Exécuter la requête SQL
    # ──────────────────────────────────────────────
    cursor.execute("SELECT * FROM reunions ORDER BY date_reunion DESC")
    # ORDER BY titre ASC = trier par titre alphabétiquement (A → Z)
    # ASC = ascending = croissant.. DESC = descending = décroissant

    reunions = cursor.fetchall()
    # fetchall() récupère TOUTES les lignes du résultat et les met dans une liste Python
    # Résultat : livres = [{'id': 1, 'titre': '...', ...}, {'id': 2, ...}, ...]

    # ──────────────────────────────────────────────
    # ÉTAPE C : Fermer la connexion — TOUJOURS faire ça
    # ──────────────────────────────────────────────
    cursor.close()
    conn.close()
    # Fermer la connexion libère les ressources sur le serveur MySQL
    # Si tu ne fermes pas.. à force tu "épuises" les connexions disponibles
    # et MySQL refusera les nouvelles connexions

    # ──────────────────────────────────────────────
    # ÉTAPE D : Envoyer les données au template HTML
    # ──────────────────────────────────────────────
    return render_template("index.html", meetings=reunions)
    # render_template va chercher "index.html" dans le dossier templates/
    # meetings=reunions: on passe la liste de réunions au template
    # Dans le template on pourra utiliser {{ meetings }} ou faire un {% for meeting in meetings %}


# ─── Route ajouter — gère GET (afficher le formulaire) ET POST (traiter les données) ───
@app.route("/nouvelle", methods=["GET", "POST"])
def nouvelle():
    # methods=["GET", "POST"] indique que cette route accepte les deux méthodes HTTP
    # Sans ça Flask n'accepte que GET par défaut

    erreurs = []
    # Liste pour collecter les messages d'erreur de validation

    date_val = None  # Contiendra l'objet date pour MySQL
    heure_val = None # Contiendra l'objet date pour MySQL

    if request.method == "POST":
        # ──────────────────────────────────────────────
        # On est ici seulement si le formulaire a été soumis
        # ──────────────────────────────────────────────

        # Récupérer les données envoyées par le formulaire
        titre           = request.form.get("titre",  "").strip()
        date_saisie     = request.form.get("date", "").strip()
        heure           = request.form.get("heure",  "").strip()
        # OPTIONNEL
        lieu            = request.form.get("lieu",  "").strip()
        # OPTIONNEL
        type_reunion    = request.form.get("type_reunion",  "").strip()
        ordre           = request.form.get("ordre", "").strip() 
        # OPTIONNEL et pas encore de validation côté serveur
        president       = request.form.get("president", "").strip() 
        # OPTIONNEL
        secretaire       = request.form.get("secretaire", "").strip() 
        # .get("cle", "") = retourne "" si le champ est absent plutôt qu'une erreur
        # .strip() = supprime les espaces inutiles au début et à la fin

        # ──────────────────────────────────────────────
        # Validation des données — côté serveur
        # ──────────────────────────────────────────────
        # On ne fait jamais confiance aux données du formulaire
        # Même si on a mis "required" en HTML.. quelqu'un peut désactiver ça dans son navigateur
        if not titre:
            erreurs.append("Le titre est obligatoire.")
        elif len(titre) > 200:
            erreurs.append("Le titre ne peut pas dépasser 200 caractères.")

        if not date_saisie:
            erreurs.append("La date de la réunion est obligatoire.")
            # Exécuté si l'utilisateur n'a rien mis
        else:
            try:
                # Si l'utilisateur met quelque chose
                # On tente de convertir la chaîne "AAAA-MM-JJ" en objet date
                # %Y = Année sur 4 chiffres, %m = Mois (01 à 12), %d = Jour (01 à 31)
                date_val = datetime.strptime(date_saisie, "%Y-%m-%d").date()
            except ValueError:
                # Si la date n'existe pas (ex: 2026-02-31) ou si le format est altéré
                erreurs.append("La date saisie n'est pas valide (format attendu : AAAA-MM-JJ).")

        if heure: 
            try:
                # On tente de convertir la chaîne "HH:MM" en objet time
                # %H = heure (00 à 23), %M = minute (00 à 59)
                heure_val = datetime.strptime(heure, "%H:%M").time()
            except ValueError:
                # Si Python lève une erreur, le format ou les chiffres sont faux
                erreurs.append("L'heure saisie n'est pas valide (format attendu : HH:MM).")
        # L'heure est optionnelle
        # Si l'heure n'a été saisie heure_val reste à none
        
        if len(lieu) > 200:
            erreurs.append("Le lieu ne peut pas dépasser 200 caractères.")

        if not type_reunion:
            erreurs.append("Le type de la réunion est obligatoire.")


        if len(president) > 150:
            erreurs.append("Le nom du prédident de séance ne peut pas dépasser 150 caractères.")


        if not secretaire:
            erreurs.append("Le nom du secrétaire est obligatoire.")
        elif len(secretaire) > 150:
            erreurs.append("Le titre ne peut pas dépasser 150 caractères.")

        # ──────────────────────────────────────────────
        # Si pas d'erreurs → insérer en base et rediriger
        # ──────────────────────────────────────────────
        if not erreurs:
            conn   = get_connection()
            cursor = conn.cursor()

            # annee_val = None si le champ est vide.. MySQL stockera NULL
            lieu_val = lieu if lieu else None
            president_val = president if president else None
            

            cursor.execute(
                "INSERT INTO reunions (titre, date_reunion, heure_debut, lieu, type_reunion, ordre_du_jour, president, secretaire) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (titre, date_val,heure_val, lieu_val, type_reunion, ordre, president_val, secretaire)
                # Les %s sont remplacés par les vraies valeurs de façon sécurisée
                # Protection automatique contre l'injection SQL
            )

            conn.commit()
            # OBLIGATOIRE — sans commit() l'INSERT ne sera pas sauvegardé

            cursor.close()
            conn.close()

            # Rediriger vers la page d'accueil
            # redirect() envoie au navigateur un code HTTP 302 "va voir cette autre URL"
            # url_for("accueil") génère l'URL "/" depuis le nom de la fonction
            return redirect(url_for("accueil"))

    # ──────────────────────────────────────────────
    # On arrive ici dans deux cas :
    # 1. Requête GET (première visite de la page)
    # 2. Requête POST avec des erreurs de validation
    # ──────────────────────────────────────────────
    return render_template("nouvelle.html", erreurs=erreurs)

# ───────────────────────────────────────────────────────
# ROUTE 3 : Détail d'une reunion
# URL : GET /reunion/<id>
# ───────────────────────────────────────────────────────
@app.route("/reunion/<int:reunion_id>")
def reunion(reunion_id):
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Première requête SELECT pour les reunions
    cursor.execute("SELECT * FROM reunions WHERE id = %s", (reunion_id,))
    reunion_recup  = cursor.fetchone()
    # Deuxième requête SELECT pour les présents
    cursor.execute("SELECT * FROM participants WHERE reunion_id=%s", (reunion_id,))
    presents = cursor.fetchall()
    cursor.execute("SELECT interventions.id,interventions.contenu,interventions.date_intervention,participants.nom,participants.prenom,participants.fonction FROM    interventions JOIN    participants ON interventions.participant_id = participants.id WHERE   interventions.reunion_id = %s ORDER BY interventions.date_intervention ASC", (reunion_id,))
    interventions = cursor.fetchall()


    cursor.close()
    conn.close()

    if reunion_recup is None:
        return render_template("404.html"), 404

    return render_template("seance.html", reunion=reunion_recup, presents=presents, interventions=interventions)


# ───────────────────────────────────────────────────────
# ROUTE 4 : Ajouter présent
# URL : GET /reunion/<id>
# ───────────────────────────────────────────────────────
@app.route('/reunion/<int:reunion_id>/present', methods=["POST"])
def ajouter(reunion_id):

    erreurs = []
    fonction_val = None  # Contiendra la fonction pour MySQL

    # ──────────────────────────────────────────────
    # On est ici seulement si le formulaire a été soumis
    # ──────────────────────────────────────────────

     # Récupérer les données envoyées par le formulaire
    prenom_present     = request.form.get("prenom", "").strip()
    nom_present        = request.form.get("nom",  "").strip()
    fonction           = request.form.get("fonction",  "").strip()

    if not prenom_present:
        erreurs.append("Le prénom est obligatoire.")
    elif len(prenom_present) > 150:
        erreurs.append("Le prénom ne peut pas dépasser 150 caractères.")

    if not nom_present:
        erreurs.append("Le nom est obligatoire.")
    elif len(nom_present) > 50:
        erreurs.append("Le nom ne peut pas dépasser 50 caractères.")


   
        # ──────────────────────────────────────────────
        # Si pas d'erreurs → insérer en base et rediriger
        # ──────────────────────────────────────────────
    if not erreurs:
        conn   = get_connection()
        cursor = conn.cursor()
        
        fonction_val = fonction if fonction else None
        

        cursor.execute("INSERT INTO participants (reunion_id, nom, prenom, fonction) VALUES (%s,%s,%s,%s)",
                       (reunion_id, nom_present, prenom_present, fonction_val)
                       )

        conn.commit()
        # OBLIGATOIRE — sans commit() l'INSERT ne sera pas sauvegardé

        cursor.close()
        conn.close()

        return redirect(url_for("reunion", reunion_id=reunion_id))
    
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reunions WHERE id = %s", (reunion_id,))
    reunion_rec  = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template("seance.html", reunion=reunion_rec, errors=erreurs)


# ───────────────────────────────────────────────────────
# ROUTE 5 : Enregistrer une intervention
# URL : GET /reunion/<id>
# ───────────────────────────────────────────────────────
@app.route('/reunion/<int:reunion_id>/intervention', methods=["POST"])
def enregistrer(reunion_id):
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reunions WHERE id = %s", (reunion_id,))
    reunion_rec  = cursor.fetchone()
    cursor.close()
    conn.close()
    
    erreurs = []

     # Récupérer les données envoyées par le formulaire
    participant_id = request.form.get("participant_id", "")
    contenu        = request.form.get("contenu", "").strip()

    if not participant_id:
        erreurs.append("Le nom de l'intervenant est obligatoire.")
    

    if not contenu:
        erreurs.append("Le contenu de l'intervention est obligatoire.")
    elif len(contenu) < 150:
        erreurs.append("L'intervention doit dépasser au moins 150 caractères.")

    if not erreurs:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interventions (reunion_id, participant_id, contenu) VALUES (%s,%s,%s)",
                       (reunion_id, participant_id, contenu)
                       )
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("reunion", reunion_id=reunion_id))
    

    
    return render_template("seance.html",reunion=reunion_rec, dioums=erreurs)

# ───────────────────────────────────────────────────────
# ROUTE 6 : Clôturer la réunion (UPDATE statut)
# URL : GET ou POST /reunion/<id>/terminer
# ───────────────────────────────────────────────────────
@app.route("/reunion/<int:reunion_id>/terminer", methods=["GET", "POST"])
def terminer(reunion_id):
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reunions SET statut='terminée' WHERE id=%s", (reunion_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("reunion", reunion_id=reunion_id))

# ───────────────────────────────────────────────────────
# ROUTE 7 : Afficher le procès-verbal
# URL : GET /reunion/<id>/pv
# ───────────────────────────────────────────────────────
@app.route("/reunion/<int:reunion_id>/pv")
def pv(reunion_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reunions WHERE id=%s", (reunion_id,))
    reunion = cursor.fetchone()
    # Deuxième requête SELECT pour les présents
    cursor.execute("SELECT * FROM participants WHERE reunion_id=%s", (reunion_id,))
    presents = cursor.fetchall()
    cursor.execute("SELECT interventions.id,interventions.contenu,interventions.date_intervention,participants.nom,participants.prenom,participants.fonction FROM    interventions JOIN    participants ON interventions.participant_id = participants.id WHERE   interventions.reunion_id = %s ORDER BY interventions.date_intervention ASC", (reunion_id,))
    interventions = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("pv.html", dadjer=reunion, gniteew=presents, kaddu=interventions)


if __name__ == "__main__":
    app.run(debug=True)