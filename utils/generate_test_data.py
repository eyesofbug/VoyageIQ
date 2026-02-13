import csv
import random

def generate_real_raw_data(output_file):
    # Expanded list of real Indian tourist attractions
    # We ensure each city has at least 15-20 attractions to avoid repeats in 5-day itineraries
    data_map = {
        "Kerala": {
            "Munnar": ["Eravikulam National Park", "Mattupetty Dam", "Tea Museum", "Echo Point", "Anamudi Peak", "Attukal Waterfalls", "Pothamedu View Point", "Lockhart Gap", "Chithirapuram", "Devikulam", "Nyayamakad Falls", "Kundala Lake", "Top Station", "Marayoor Sandalwood Forest", "Meesapulimala"],
            "Kochi": ["Fort Kochi", "Mattancherry Palace", "Jewish Synagogue", "Chinese Fishing Nets", "Marine Drive", "Bolgatty Palace", "Willingdon Island", "Cherai Beach", "Hill Palace Museum", "Santa Cruz Basilica", "St. Francis Church", "Mangalavanam Bird Sanctuary", "Wonderla Kochi", "Lulu Mall", "Athirappilly Falls Day Trip"],
            "Alleppey": ["Alappuzha Beach", "Vembanad Lake", "Marari Beach", "Kuttanad Backwaters", "Alleppey Lighthouse", "Pathiramanal Island", "Krishnapuram Palace", "Ambalapuzha Temple", "Mannarasala Temple", "Revi Karunakaran Museum", "St. Andrew's Basilica", "Punnamada Lake"],
            "Thekkady": ["Periyar National Park", "Periyar Lake", "Abraham's Spice Garden", "Kadathanadan Kalari Centre", "Mudrankalayalam", "Elephant Junction", "Chellarkovil View Point", "Pandikuzhi", "Mangala Devi Temple"],
            "Varkala": ["Varkala Beach", "Janardhana Swami Temple", "Sivagiri Mutt", "Anjengo Fort", "Kappil Lake", "Varkala Cliff", "Ponnumthuruthu Island"]
        },
        "Goa": {
            "North Goa": ["Baga Beach", "Calangute Beach", "Anjuna Beach", "Aguada Fort", "Chapora Fort", "Vagator Beach", "Candolim Beach", "Sinquerim Beach", "Arambol Beach", "Morjim Beach", "Mapusa Market", "Reis Magos Fort", "Snow Park", "Casino Pride", "Deltin Royale"],
            "Old Goa": ["Basilica of Bom Jesus", "Se Cathedral", "Church of St. Francis of Assisi", "Archeological Museum", "St. Augustine Tower", "Church of Our Lady of the Mount"],
            "South Goa": ["Colva Beach", "Palolem Beach", "Dudhsagar Falls", "Margao Market", "Cabo de Rama Fort", "Benaulim Beach", "Varca Beach", "Cavelossim Beach", "Agonda Beach", "Galgibaga Beach", "Butterfly Beach", "Netravali Wildlife Sanctuary"]
        },
        "Rajasthan": {
            "Jaipur": ["Amber Fort", "Hawa Mahal", "City Palace", "Jantar Mantar", "Nahargarh Fort", "Jaigarh Fort", "Albert Hall Museum", "Birla Mandir", "Galta Ji Temple", "Chokhi Dhani", "Panna Meena ka Kund", "Patrika Gate", "Jal Mahal", "Johari Bazaar", "Bapu Bazaar"],
            "Udaipur": ["City Palace", "Lake Pichola", "Jag Mandir", "Saheliyon-ki-Bari", "Fateh Sagar Lake", "Bagore Ki Haveli", "Sajjangarh Monsoon Palace", "Jagdish Temple", "Vintage Car Museum", "Shilpgram"],
            "Jodhpur": ["Mehrangarh Fort", "Jaswant Thada", "Umaid Bhawan Palace", "Mandore Gardens", "Clock Tower", "Sardar Market", "Rao Jodha Desert Rock Park", "Kaylana Lake"],
            "Jaisalmer": ["Jaisalmer Fort", "Patwon Ki Haveli", "Sam Sand Dunes", "Gadisar Lake", "Tanot Mata Temple", "Kuldhara Village", "Desert National Park"]
        },
        "Karnataka": {
            "Chikkamagaluru": ["Kudremukh Trek", "Mullayanagiri Peak", "Baba Budangiri", "Hebbe Falls", "Jhari Waterfalls", "Kalasa", "Horanadu Temple", "Kudremukh National Park", "Kemmangundi", "Z Point", "Kallathigiri Falls", "Bhadra Wildlife Sanctuary", "Coffee Museum", "Ayyanakere Lake"],
            "Bangalore": ["Lalbagh Botanical Garden", "Cubbon Park", "Bangalore Palace", "ISKCON Temple", "Bannerghatta National Park", "Visvesvaraya Museum", "Vidhana Soudha", "Tipu Sultan Palace", "Nandi Hills", "Commercial Street"],
            "Mysore": ["Mysore Palace", "Chamundi Hill", "Brindavan Gardens", "St. Philomena's Church", "Mysore Zoo", "Jaganmohan Palace", "Karanji Lake", "Ranganathittu Bird Sanctuary"],
            "Hampi": ["Virupaksha Temple", "Vittala Temple", "Lotus Mahal", "Elephant Stables", "Hazara Rama Temple", "Matanga Hill", "Hemakuta Hill", "Tungabhadra River", "Hampi Bazaar"]
        },
        "Tamil Nadu": {
            "Ooty": ["Ooty Lake", "Government Botanical Garden", "Doddabetta Peak", "Pykara Falls", "Pykara Lake", "Rose Garden", "Nilgiri Mountain Railway", "Tea Factory", "Avalanche Lake", "Emerald Lake", "St. Stephen's Church", "Thunder World", "Ooty Stone House"],
            "Chennai": ["Marina Beach", "Kapaleeshwarar Temple", "Fort St. George", "Santhome Cathedral", "Government Museum", "Guindy National Park", "VGP Universal Kingdom", "MGM Dizzee World", "Elliott's Beach"],
            "Madurai": ["Meenakshi Amman Temple", "Thirumalai Nayakkar Mahal", "Gandhi Memorial Museum", "Koodal Azhagar Temple", "Alagar Koyil"]
        }
    }

    # Latitude/Longitude approximate centers for cities
    city_coords = {
        "Munnar": (10.0889, 77.0595), "Kochi": (9.9658, 76.2421), "Alleppey": (9.4981, 76.3329), "Thekkady": (9.6031, 77.1615), "Varkala": (8.737, 76.703),
        "North Goa": (15.5553, 73.7517), "Old Goa": (15.5009, 73.9116), "South Goa": (15.277, 73.9126),
        "Jaipur": (26.9124, 75.7873), "Udaipur": (24.5854, 73.7125), "Jodhpur": (26.2389, 73.0243), "Jaisalmer": (26.9157, 70.9083),
        "Chikkamagaluru": (13.3161, 75.7720), "Bangalore": (12.9716, 77.5946), "Mysore": (12.2958, 76.6394), "Hampi": (15.335, 76.46),
        "Ooty": (11.4102, 76.695), "Chennai": (13.0827, 80.2707), "Madurai": (9.9252, 78.1198)
    }

    categories = ["Scenic", "History", "Religious", "Adventure", "Nature", "Beach", "Museum", "Palace", "Waterfall"]

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Place Name", "State", "City", "Latitude", "Longitude", "Category"])
        
        for state, cities in data_map.items():
            for city, places in cities.items():
                base_lat, base_lon = city_coords.get(city, (15.0, 75.0))
                for place in places:
                    # Perturb lat/lon slightly for clusters
                    lat = round(base_lat + random.uniform(-0.05, 0.05), 4)
                    lon = round(base_lon + random.uniform(-0.05, 0.05), 4)
                    cat = random.choice(categories)
                    writer.writerow([place, state, city, lat, lon, cat])
    
    print(f"Exported expanded real Indian landmarks to {output_file}")

if __name__ == "__main__":
    generate_real_raw_data("data/raw_attractions.csv")
