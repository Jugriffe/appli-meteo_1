from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ===== TES FONCTIONS MÉTÉO (on reprend le code) =====

def trouver_coordonnees(ville):
    """Trouve les coordonnées GPS d'une ville"""
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": ville,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    
    headers = {"User-Agent": "AppMeteo/1.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 0:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                nom_complet = result["display_name"]
                
                return lat, lon, nom_complet
        return None
            
    except Exception as e:
        return None

def obtenir_meteo(latitude, longitude):
    """Récupère la météo"""
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,rain,weather_code,wind_speed_10m",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            current = data["current"]
            
            return {
                "temperature": current["temperature_2m"],
                "windspeed": current["wind_speed_10m"],
                "weathercode": current["weather_code"],
                "precipitation": current["precipitation"],
                "rain": current["rain"]
            }
        return None
            
    except Exception as e:
        return None

def interpreter_weathercode(code):
    """Interprète le code météo"""
    codes = {
        0: "☀️ Ciel dégagé",
        1: "🌤️ Plutôt dégagé",
        2: "⛅ Partiellement nuageux",
        3: "☁️ Couvert",
        45: "🌫️ Brouillard",
        48: "🌫️ Brouillard givrant",
        51: "🌦️ Bruine légère",
        53: "🌦️ Bruine modérée",
        55: "🌧️ Bruine dense",
        61: "🌧️ Pluie légère",
        63: "🌧️ Pluie modérée",
        65: "🌧️ Pluie forte",
        71: "🌨️ Neige légère",
        73: "🌨️ Neige modérée",
        75: "❄️ Neige forte",
        80: "🌦️ Averses légères",
        81: "🌧️ Averses modérées",
        82: "⛈️ Averses violentes",
        95: "⛈️ Orage",
    }
    return codes.get(code, "🌡️ Météo inconnue")

def generer_conseils(meteo):
    """Génère tous les conseils en un seul dictionnaire"""
    conseils = {
        "meteo": interpreter_weathercode(meteo['weathercode']),
        "temperature": [],
        "vent": [],
        "pluie": []
    }
    
    # Conseils température
    temp = meteo['temperature']
    if temp < -5:
        conseils["temperature"].append("🧊 TRÈS FROID ! Gros manteau d'hiver indispensable")
    elif temp < 5:
        conseils["temperature"].append("🧥 Manteau ou grosse veste recommandée")
    elif temp < 10:
        conseils["temperature"].append("🧥 Veste chaude conseillée")
    elif temp < 15:
        conseils["temperature"].append("🧥 Veste ou pull conseillé")
    elif temp < 20:
        conseils["temperature"].append("👕 T-shirt + veste légère (au cas où)")
    elif temp < 25:
        conseils["temperature"].append("👕 T-shirt, temps agréable !")
    else:
        conseils["temperature"].append("🩳 Tenue légère, il fait chaud !")
    
    # Conseils vent
    vent = meteo['windspeed']
    if vent > 40:
        conseils["vent"].append("💨 VENT VIOLENT ! Attention aux objets volants")
    elif vent > 25:
        conseils["vent"].append("💨 Vent fort, prévois une veste bien fermée")
    elif vent > 15:
        conseils["vent"].append("💨 Petit vent, couvre-toi un peu plus")
    
    # Conseils pluie
    code = meteo['weathercode']
    precip = meteo['precipitation']
    
    if code in [95, 96, 99]:
        conseils["pluie"].append("⛈️ ORAGE ! Reste à l'intérieur si possible")
        conseils["pluie"].append("☔ Imperméable + parapluie solide recommandés")
    elif code in [65, 82]:
        conseils["pluie"].append("🌧️ FORTE PLUIE !")
        conseils["pluie"].append("☔ Imperméable indispensable + parapluie")
    elif code in [63, 81]:
        conseils["pluie"].append("🌧️ Pluie modérée")
        conseils["pluie"].append("☔ Parapluie ou imperméable recommandé")
    elif code in [61, 80, 51, 53, 55]:
        conseils["pluie"].append("🌦️ Pluie légère / bruine")
        conseils["pluie"].append("🧥 Manteau à capuche suffisant (ou petit parapluie)")
    elif code in [71, 73, 75, 77, 85, 86]:
        conseils["pluie"].append("❄️ NEIGE prévue !")
        conseils["pluie"].append("🧥 Manteau imperméable + gants + bonnet")
    
    if precip > 0 and not conseils["pluie"]:
        conseils["pluie"].append(f"💧 Précipitations légères ({precip} mm)")
    
    return conseils

# ===== ROUTES WEB =====

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/meteo', methods=['POST'])
def meteo():
    """API qui renvoie la météo"""
    ville = request.json.get('ville')
    
    if not ville:
        return jsonify({"erreur": "Ville manquante"}), 400
    
    # Trouver coordonnées
    coordonnees = trouver_coordonnees(ville)
    if not coordonnees:
        return jsonify({"erreur": f"Ville '{ville}' introuvable"}), 404
    
    lat, lon, nom_complet = coordonnees
    
    # Récupérer météo
    meteo_data = obtenir_meteo(lat, lon)
    if not meteo_data:
        return jsonify({"erreur": "Impossible de récupérer la météo"}), 500
    
    # Générer conseils
    conseils = generer_conseils(meteo_data)
    
    # Renvoyer tout
    return jsonify({
        "ville": nom_complet,
        "temperature": meteo_data['temperature'],
        "vent": meteo_data['windspeed'],
        "precipitation": meteo_data['precipitation'],
        "conseils": conseils
    })

# ===== LANCEMENT DU SERVEUR =====
if __name__ == '__main__':
    import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

