import requests
import pandas as pd
from app.core.config_loader import *

SPOKE_BASE_URL = system_config['SPOKE_BASE_URL']
nodes = [
  "Disease",
  "Symptom",
  "Compound",
  "SideEffect",
  "Gene",
  "Protein"
]

names = []
ids = []
types = []

for node in nodes:
    search_url = f"{SPOKE_BASE_URL}/search/{node}/*"
    response = requests.get(search_url)

    if response.status_code == 200:
        genes = response.json()

        for gene in genes:
            name = gene['name']
            type = gene['node_type']
            id = gene['identifier']
            names.append(name)
            ids.append(id)
            types.append(type)
    
        df = pd.DataFrame({
            "name": names,
            "id": ids,
            "type": types
        })

        df.to_csv('data_all.csv', mode="w")