import json

with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

bodenprobe_preis = 15

std_auftrag_name = "Standard-Auftrag"

customers_per_site = 10

# Suchkriterien für die verschiedenen Klassen in der Datenbank
suchkriterien = {
    "kun": ['nachname', 'vorname', 'id', 'email', 'wohnort', 'vorname+nachname', 'nachname+vorname'],
    "auf": ['id', 'label_name'],
    "bod": ['id', 'label_name'],
}

# Und die Daten, die dargestellt werden sollen
suchergebniss_spalten = {
    "kun": ['nachname', 'vorname', 'email', 'wohnort'],
    "auf": ['label_name'],
    "bod": ['label_name'],
}

# Damit auf die Details Seiten der Klassen auch verlinkt werden kann
baselink = {
    "kun": "kunde_details",
    "auf": "auftrag_details",
    "bod": "bodenprobe_details",
}

microsoft_word_installed = config['microsoft-word-installed']

production: bool = config['production']

relevant_elements = [
    'Cd',
    'Cu',
    'Pb',
    'Zn',
    'Cr',
    'Ni',
    'As',
]

used_elements = [element.lower() for element in relevant_elements]
