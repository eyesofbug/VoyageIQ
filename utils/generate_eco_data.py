import csv

def generate_eco_data(output_file):
    eco_destinations = [
        # Name, State, District, Entry Fee, Approximate Duration (hours)
        ["Ali Bedni Bugyal Trek", "Uttarakhand", "Chamoli", 150, 48],
        ["Deoriatal Chandrashila Trek", "Uttarakhand", "Rudraprayag", 200, 36],
        ["Har Ki Dun Trek", "Uttarakhand", "Uttarkashi", 250, 72],
        ["Valley of Flowers", "Uttarakhand", "Chamoli", 150, 6],
        ["Periyar Nature Walk", "Kerala", "Thekkady", 300, 3],
        ["Bamboo Rafting Periyar", "Kerala", "Thekkady", 2000, 8],
        ["Eravikulam Trail", "Kerala", "Munnar", 125, 4],
        ["Mawphlang Sacred Grove", "Meghalaya", "East Khasi Hills", 100, 2],
        ["Agumbe Rainforest Trail", "Karnataka", "Shimoga", 50, 5],
        ["Kudremukh Trek", "Karnataka", "Chikkamagaluru", 200, 8],
        ["Silent Valley Trail", "Kerala", "Palakkad", 100, 5],
        ["Nandadevi Biosphere Trail", "Uttarakhand", "Chamoli", 500, 10],
        ["Sundarbans Boat Safari", "West Bengal", "South 24 Parganas", 500, 12],
        ["Kanha Nature Trail", "Madhya Pradesh", "Mandla", 200, 3],
        ["Jim Corbett Jeep Safari", "Uttarakhand", "Nainital", 1500, 4],
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "State", "District", "Entry Fee", "Duration"])
        writer.writerows(eco_destinations)
    print(f"Generated eco-tourism data in {output_file}")

if __name__ == "__main__":
    generate_eco_data("data/raw_eco_tourism.csv")
