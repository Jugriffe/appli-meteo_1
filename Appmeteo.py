import requests

print("🌤️  APP MÉTÉO - CONSEILS VESTIMENTAIRES")
print("=" * 50)

# ===== FONCTION : TROUVER LES COORDONNÉES D'UNE VILLE =====
def trouver_coordonnees(ville):
    """
    Recherche les coordonnées GPS d'une ville
    Renvoie : (latitude, longitude, nom_complet) ou None si introuvable
    """
    print(f"\n🔍 Recherche des coordonnées de {ville}...")
    
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": ville,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    
    headers = {
        "User-Agent": "AppMeteo/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 0:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                nom_complet = result["display_name"]
                
                print(f"✅ Trouvée : {nom_complet}")
                print(f"📍 Coordonnées : {lat:.2f}°N, {lon:.2f}°E")
                
                return lat, lon, nom_complet
            else:
                print(f"❌ Ville '{ville}' introuvable")
                print("💡 Vérifie l'orthographe ou essaie une autre ville")
                return None
        else:
            print(f"❌ Erreur de connexion ({response.status_code})")
            return None
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

# ===== FONCTION : RÉCUPÉRER LA MÉTÉO =====
def obtenir_meteo(latitude, longitude):
    """
    Récupère la météo actuelle pour des coordonnées données
    AVEC les données de pluie !
    """
    print("\n🌐 Récupération de la météo...")
    
    url = "https://api.open-meteo.com/v1/forecast"
    
    # ⭐ CORRECTION : On demande les bonnes variables
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
            
            # ⭐ On récupère les données depuis "current"
            current = data["current"]
            
            meteo_complete = {
                "temperature": current["temperature_2m"],
                "windspeed": current["wind_speed_10m"],
                "weathercode": current["weather_code"],
                "precipitation": current["precipitation"],
                "rain": current["rain"]
            }
            
            return meteo_complete
        else:
            print(f"❌ Erreur météo ({response.status_code})")
            return None
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print(f"💡 Données reçues : {data if 'data' in locals() else 'Aucune'}")
        return None

# ===== FONCTION : INTERPRÉTER LE CODE MÉTÉO =====
def interpreter_weathercode(code):
    """
    Traduit le code météo en description
    Codes WMO : https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
    """
    codes = {
        0: "☀️ Ciel dégagé",
        1: "🌤️ Plutôt dégagé",
        2: "⛅ Partiellement nuageux",
        3: "☁️ Couvert",
        45: "🌫️ Brouillard",
        48: "🌫️ Brouillard givrant",
        51: "🌦️ Bruine légère",
        53: "🌦️ Bruine modérée",
        55: "🌧️ Bruine forte",
        61: "🌧️ Pluie légère",
        63: "🌧️ Pluie modérée",
        65: "🌧️ Pluie forte",
        71: "🌨️ Neige légère",
        73: "🌨️ Neige modérée",
        75: "❄️ Neige forte",
        80: "🌦️ Averses légères",
        81: "⛈️ Averses modérées",
        82: "⛈️ Averses violentes",
        95: "⛈️ Orage",
        96: "⛈️ Orage avec grêle légère",
        99: "⛈️ Orage avec forte grêle"
    }
    
    return codes.get(code, f"Code {code}")

# ===== FONCTION : CONSEILS PLUIE =====
def conseils_pluie(weathercode, precipitation, rain):
    """
    Donne des conseils spécifiques pour la pluie
    """
    # Codes de pluie : 51-55 (bruine), 61-65 (pluie), 80-82 (averses), 95-99 (orages)
    codes_pluie = [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]
    
    if weathercode in codes_pluie or precipitation > 0 or rain > 0:
        print("\n☔ PROTECTION PLUIE :")
        print("-" * 50)
        
        # Orage
        if weathercode >= 95:
            print("  ⛈️ ORAGE ! Reste à l'intérieur si possible")
            print("  ☔ Imperméable + parapluie INDISPENSABLES")
        
        # Pluie forte ou averses violentes
        elif weathercode in [65, 82] or precipitation > 5 or rain > 5:
            print("  🌧️ FORTE PLUIE prévue")
            print("  ☔ Imperméable recommandé + parapluie")
        
        # Pluie modérée
        elif weathercode in [63, 81] or precipitation > 2 or rain > 2:
            print("  🌧️ Pluie modérée")
            print("  ☔ Parapluie recommandé ou manteau imperméable")
        
        # Pluie légère / bruine
        elif weathercode in [51, 53, 61, 80] or precipitation > 0:
            print("  🌦️ Pluie légère / bruine")
            print("  🧥 Manteau à capuche suffisant (ou petit parapluie)")
        
        # Affichage quantité
        if precipitation > 0:
            print(f"  💧 Précipitations : {precipitation} mm")
    else:
        # Pas de pluie
        return False  # Indique qu'il n'y a pas de pluie
    
    return True  # Indique qu'il y a de la pluie

# ===== FONCTION : CONSEILS TEMPÉRATURE & VENT =====
def conseils_vestimentaires(temperature, vitesse_vent):
    """
    Génère des conseils en fonction de la température et du vent
    """
    print("\n👔 CONSEILS VESTIMENTAIRES :")
    print("-" * 50)
    
    # Conseil température
    if temperature < 0:
        print("  🥶 TRÈS FROID ! Manteau d'hiver + gants + bonnet")
    elif temperature < 5:
        print("  🧥 Manteau chaud + écharpe obligatoires")
    elif temperature < 10:
        print("  🧥 Manteau ou grosse veste recommandée")
    elif temperature < 15:
        print("  🧥 Veste ou pull conseillé")
    elif temperature < 20:
        print("  👕 T-shirt + veste légère (au cas où)")
    elif temperature < 25:
        print("  👕 T-shirt, temps agréable !")
    else:
        print("  🩳 Tenue légère, il fait chaud !")
    
    # Conseil vent
    if vitesse_vent > 40:
        print("  💨 VENT VIOLENT ! Attention aux objets volants")
    elif vitesse_vent > 25:
        print("  💨 Vent fort, prévois une veste bien fermée")
    elif vitesse_vent > 15:
        print("  💨 Petit vent, couvre-toi un peu plus")

# ===== PROGRAMME PRINCIPAL =====
ville = input("\n📍 Entre le nom de ta ville : ")

# Étape 1 : Trouver les coordonnées
coordonnees = trouver_coordonnees(ville)

if coordonnees:
    lat, lon, nom_complet = coordonnees
    
    # Étape 2 : Récupérer la météo
    meteo = obtenir_meteo(lat, lon)
    
    if meteo:
        # Étape 3 : Afficher les données
        print("\n📊 MÉTÉO ACTUELLE :")
        print("-" * 50)
        print(f"  {interpreter_weathercode(meteo['weathercode'])}")
        print(f"  🌡️  Température : {meteo['temperature']}°C")
        print(f"  💨 Vent : {meteo['windspeed']} km/h")
        
        # Étape 4 : Conseils PLUIE (en premier !)
        y_a_de_la_pluie = conseils_pluie(
            meteo['weathercode'], 
            meteo['precipitation'], 
            meteo['rain']
        )
        
        # Étape 5 : Conseils température & vent
        conseils_vestimentaires(meteo['temperature'], meteo['windspeed'])
        
        # Message final si pas de pluie
        if not y_a_de_la_pluie:
            print("\n☀️ Pas de pluie prévue, tu peux laisser le parapluie !")

print("\n" + "=" * 50)
print("✨ Merci d'avoir utilisé l'app météo !")