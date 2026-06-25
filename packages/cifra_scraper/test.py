
import requests

# Teste com música que contenha acentos
response = requests.get('http://localhost:3000/artists/joao-gilberto/songs/chega-de-saudade')
data = response.json()

# Imprime a cifra formatada
for line in data['cifra']:
    print(line)
