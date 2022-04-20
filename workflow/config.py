import json

with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

soil_sample_price: float = 15.0

std_auftrag_name: str = "Standard-Auftrag"

customers_per_site: int = 10

# search criteria for the different models in the database
search_criteria = {
    "kun": ['nachname', 'vorname', 'id', 'email', 'wohnort', 'vorname+nachname', 'nachname+vorname'],
    "auf": ['id', 'label_name'],
    "bod": ['id', 'label_name'],
}

# specify which data to display
search_result_columns = {
    "kun": ['nachname', 'vorname', 'email', 'wohnort'],
    "auf": ['label_name'],
    "bod": ['label_name'],
}

# to be able to link to the details sites of the other models
baselink = {
    "kun": "kunde_details",
    "auf": "auftrag_details",
    "bod": "bodenprobe_details",
}

microsoft_word_installed: bool = config['microsoft-word-installed']

production: bool = config['production']

relevant_elements = [
    'Cd',
    'Cu',
    'Pb',
    'Zn',
    'Ni',
    'As',
]

used_elements = [element.lower() for element in relevant_elements]

template_filename: str = 'tpl_6.docx'

invoice_tpl_filename: str = 'invoice_1.docx'

invoice_descs: dict = {
    'soil_sample': "Schwermetallanalyse As, Cd, Cu, Ni, Pb und Zn mittels RFA",
}
