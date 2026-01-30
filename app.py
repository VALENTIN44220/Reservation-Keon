from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_moi'  # Nécessaire pour les sessions

# Fichiers pour stocker les données
RESERVATIONS_FILE = "reservations.json"
USERS_FILE = "users.json"

materiels = [
    {"id": 5, "nom": "BG-Bureau stock", "etat": "disponible"},
    {"id": 6, "nom": "BG-Citroen 028-YB", "etat": "disponible"},
    {"id": 7, "nom": "BG-Peugeot 575 CA", "etat": "disponible"},
    {"id": 8, "nom": "Peugeot 739 GC", "etat": "disponible"},
    {"id": 9, "nom": "BGN- Drone DJI", "etat": "disponible"},
    {"id": 10, "nom": "BGN- Jabra Speak", "etat": "disponible"},
    {"id": 11, "nom": "BGN-PHONEBOX1 (1p)", "etat": "disponible"},
    {"id": 12, "nom": "BGN- PHONEBOX2 (1p)", "etat": "disponible"},
    {"id": 13, "nom": "BGN- Salle 1 (6-20p)", "etat": "disponible"},
    {"id": 14, "nom": "BGN-Salle 2 (3-5p)", "etat": "disponible"},
    {"id": 15, "nom": "BGN- Salle 3 (1-4p)", "etat": "disponible"},
    {"id": 16, "nom": "BGN- Salle 4 (1-4p)", "etat": "disponible"},
    {"id": 17, "nom": "BGN- Salle 5 (4-8p)", "etat": "disponible"},
    {"id": 18, "nom": "BGN- Salle 6 (4-8p.)", "etat": "disponible"},
    {"id": 19, "nom": "BGN- Salle 7 (1-2)", "etat": "disponible"},
    {"id": 20, "nom": "BGN-Videoprojecteur ACER", "etat": "disponible"},
    {"id": 22, "nom": "BNG-Videoprojecteur Mimius", "etat": "disponible"},
    {"id": 23, "nom": "MLK- Citroen ET 526 AF", "etat": "disponible"},
    {"id": 24, "nom": "MLK- Grande salle 2", "etat": "disponible"},
    {"id": 25, "nom": "MLK-Megane E-Tech", "etat": "disponible"},
    {"id": 26, "nom": "MLK-Salle bleue 2", "etat": "disponible"},
    {"id": 27, "nom": "MLK-Salle orange 2", "etat": "disponible"},
    {"id": 28, "nom": "MLK-Salle orange 3", "etat": "disponible"},
    {"id": 29, "nom": "MLK- Salle verte 3", "etat": "disponible"},
    {"id": 30, "nom": "MLK- Scenic HC-960-EP", "etat": "disponible"}
]

def charger_reservations():
    """Charge les réservations depuis le fichier JSON"""
    if os.path.exists(RESERVATIONS_FILE):
        try:
            with open(RESERVATIONS_FILE, 'r') as f:
                data = json.load(f)
                # Convertir les dates string en objets datetime
                for r in data:
                    r["debut"] = datetime.strptime(r["debut"], "%Y-%m-%d")
                    r["fin"] = datetime.strptime(r["fin"], "%Y-%m-%d")
                    # Ajouter username vide si absent (anciennes données)
                    if "username" not in r:
                        r["username"] = "Inconnu"
                return data
        except:
            return []
    return []

def sauvegarder_reservations(reservations):
    """Sauvegarde les réservations dans le fichier JSON"""
    # Convertir les objets datetime en string pour JSON
    data = []
    for r in reservations:
        data.append({
            "materiel_id": r["materiel_id"],
            "debut": r["debut"].strftime("%Y-%m-%d"),
            "fin": r["fin"].strftime("%Y-%m-%d"),
            "username": r.get("username", "Inconnu"),
            "fullname": r.get("fullname", "Utilisateur inconnu")
        })
    with open(RESERVATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def charger_utilisateurs():
    """Charge les utilisateurs depuis le fichier JSON"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def sauvegarder_utilisateurs(users):
    """Sauvegarde les utilisateurs dans le fichier JSON"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def creer_utilisateur(username, password, prenom, nom):
    """Crée un nouvel utilisateur avec mot de passe hashé"""
    users = charger_utilisateurs()
    if username in users:
        return False
    users[username] = {
        "password": generate_password_hash(password),
        "prenom": prenom,
        "nom": nom
    }
    sauvegarder_utilisateurs(users)
    return True

def verifier_utilisateur(username, password):
    """Vérifie les credentials d'un utilisateur"""
    users = charger_utilisateurs()
    if username in users:
        if check_password_hash(users[username]["password"], password):
            return users[username]
    return None

def mettre_a_jour_etats():
    """Met à jour l'état des matériels en fonction des réservations"""
    # Réinitialiser tous les états
    for m in materiels:
        m["etat"] = "disponible"
    
    # Marquer comme réservé si une réservation existe
    for r in reservations:
        for m in materiels:
            if m["id"] == r["materiel_id"]:
                m["etat"] = "réservé"
                break

def initialiser_compte_admin():
    """Crée un compte admin par défaut s'il n'existe pas"""
    users = charger_utilisateurs()
    if "admin" not in users:
        users["admin"] = {
            "password": generate_password_hash("admin123"),
            "prenom": "Admin",
            "nom": "KEON"
        }
        sauvegarder_utilisateurs(users)
        print("✅ Compte admin créé : username='admin', password='admin123'")

# Charger les réservations au démarrage
reservations = charger_reservations()
mettre_a_jour_etats()

# Initialiser le compte admin
initialiser_compte_admin()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username and password:
            user = verifier_utilisateur(username, password)
            if user:
                session['logged_in'] = True
                session['username'] = username
                session['prenom'] = user['prenom']
                session['nom'] = user['nom']
                session['fullname'] = f"{user['prenom']} {user['nom']}"
                return redirect(url_for('index'))
            else:
                return render_template("login.html", erreur="Nom d'utilisateur ou mot de passe incorrect")
        else:
            return render_template("login.html", erreur="Veuillez remplir tous les champs")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()
        prenom = request.form.get("prenom", "").strip()
        nom = request.form.get("nom", "").strip()
        
        if not all([username, password, password_confirm, prenom, nom]):
            return render_template("register.html", erreur="Veuillez remplir tous les champs")
        
        if password != password_confirm:
            return render_template("register.html", erreur="Les mots de passe ne correspondent pas")
        
        if len(password) < 6:
            return render_template("register.html", erreur="Le mot de passe doit contenir au moins 6 caractères")
        
        if creer_utilisateur(username, password, prenom, nom):
            return redirect(url_for('login'))
        else:
            return render_template("register.html", erreur="Ce nom d'utilisateur existe déjà")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    erreur = session.pop('erreur', None)  # Récupérer et supprimer le message d'erreur
    return render_template("index.html", materiels=materiels, reservations=reservations, erreur=erreur)

@app.route("/reserver/<int:id>", methods=["GET", "POST"])
def reserver(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    materiel = next(m for m in materiels if m["id"] == id)
    erreur = None

    if request.method == "POST":
        debut = datetime.strptime(request.form["debut"], "%Y-%m-%d")
        fin = datetime.strptime(request.form["fin"], "%Y-%m-%d")
        aujourd_hui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Vérifier que la date de début n'est pas dans le passé
        if debut < aujourd_hui:
            erreur = "Impossible de réserver dans le passé ! La date de début doit être aujourd'hui ou après."
            return render_template("reserver.html", materiel=materiel, erreur=erreur)

        # Vérifier que la date de fin est après la date de début
        if fin < debut:
            erreur = "La date de fin doit être après la date de début !"
            return render_template("reserver.html", materiel=materiel, erreur=erreur)

        # Vérifier les conflits de réservation
        for r in reservations:
            if r["materiel_id"] == id and not (fin < r["debut"] or debut > r["fin"]):
                # Récupérer le nom de l'utilisateur qui a déjà réservé
                reserver_par = r.get("fullname", "un autre utilisateur")
                periode = f"{r['debut'].strftime('%d/%m/%Y')} au {r['fin'].strftime('%d/%m/%Y')}"
                
                # Vérifier si la requête vient de la page d'accueil
                if request.referrer and 'reserver' not in request.referrer:
                    session['erreur'] = f"Déjà réservé par {reserver_par} du {periode}"
                    return redirect("/")
                else:
                    erreur = f"Ce matériel est déjà réservé par {reserver_par} du {periode}. Veuillez choisir d'autres dates."
                    return render_template("reserver.html", materiel=materiel, erreur=erreur)

        # Créer la réservation avec les informations de l'utilisateur
        reservations.append({
            "materiel_id": id,
            "debut": debut,
            "fin": fin,
            "username": session.get('username', 'inconnu'),
            "fullname": session.get('fullname', 'Utilisateur inconnu')
        })

        # Sauvegarder les réservations dans le fichier
        sauvegarder_reservations(reservations)
        
        materiel["etat"] = "réservé"
        return redirect("/")

    return render_template("reserver.html", materiel=materiel, erreur=erreur)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

