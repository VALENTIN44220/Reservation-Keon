from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

materiels = [
    {"id": 1, "nom": "Ordinateur portable", "etat": "disponible"},
    {"id": 2, "nom": "Vidéoprojecteur", "etat": "disponible"},
    {"id": 3, "nom": "Écran", "etat": "maintenance"}
]

reservations = []

@app.route("/")
def index():
    return render_template("index.html", materiels=materiels)

@app.route("/reserver/<int:id>", methods=["GET", "POST"])
def reserver(id):
    materiel = next(m for m in materiels if m["id"] == id)

    if request.method == "POST":
        debut = datetime.strptime(request.form["debut"], "%Y-%m-%d")
        fin = datetime.strptime(request.form["fin"], "%Y-%m-%d")

        for r in reservations:
            if r["materiel_id"] == id and not (fin < r["debut"] or debut > r["fin"]):
                return "Erreur : matériel déjà réservé sur cette période."

        reservations.append({
            "materiel_id": id,
            "debut": debut,
            "fin": fin
        })

        materiel["etat"] = "réservé"
        return redirect("/")

    return render_template("reserver.html", materiel=materiel)

if __name__ == "__main__":
    app.run(debug=True)
