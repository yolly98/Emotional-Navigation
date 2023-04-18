# docker run --name graphhopper  -d -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/andorra-latest.osm.pbf --host 0.0.0.0
import requests
import polyline
import matplotlib.pyplot as plt
import math

# Imposta la chiave API di GraphHopper
api_key = '5041e9d4-34a5-43c5-9c32-b5025464b47f'

# Imposta la posizione di partenza e di arrivo
start_point = '42.33399231261333, 12.269070539901804'
end_point = '42.332018371668575, 12.264471452495334'

# Imposta la lista di ID degli archi da evitare
avoid_edges = []

def get_street_name(point):
    # Costruisci l'URL per la richiesta di routing
    url = f'https://graphhopper.com/api/1/route?point={point}&key={api_key}&details=street_name'

    # Effettua la richiesta HTTP all'API di GraphHopper
    response = requests.get(url)

    # Verifica che la richiesta sia andata a buon fine
    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    json_data = response.json()
    print(json_data)

def get_path(start_point, end_point):
    # Costruisci l'URL per la richiesta di routing
    url = f'https://graphhopper.com/api/1/route?point={start_point}&point={end_point}&vehicle=car&locale=it&key={api_key}&avoid_edges={",".join(avoid_edges)}'

    # Effettua la richiesta HTTP all'API di GraphHopper
    response = requests.get(url)

    # Verifica che la richiesta sia andata a buon fine
    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    # Estrai il percorso dalla risposta JSON
    json_data = response.json()
    print(json_data)
    print("--------------------------")
    print(json_data['paths'])
    print("--------------------------")
    print(json_data['paths'][0]['instructions'])
    print("--------------------------")
    points = polyline.decode(json_data['paths'][0]['points'])
    print(points)

    fig, ax = plt.subplots()
    lats = []
    lons = []
    i = 0
    progress = 0
    last_point = None
    for point in points:
        if not progress == math.floor((i * 100) / (len(points))):
            progress = math.floor((i * 100) / (len(points)))
            print(f"calculation {progress}%", end="\r")

        if last_point is not None:
            ax.plot([point[0], last_point[0]], [point[1], last_point[1]], c='violet', alpha=1, linewidth=1)

        lats.append(float(point[1]))
        lons.append(float(point[0]))
        last_point = point
        i += 1

    ax.scatter(lons, lats, c='white', alpha=1, s=3)
    fig.set_facecolor('black')
    ax.set_title("Path")
    ax.axis('off')
    plt.show()

if __name__=='__main__':
    get_path(start_point, end_point)
    get_street_name(start_point)