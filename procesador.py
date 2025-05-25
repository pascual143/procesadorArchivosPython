import csv
import json
import requests
import os
from ftplib import FTP

CSV_FILE = 'datos.csv'
API_URL = 'https://httpbin.org/post'

FTP_CONFIG = {
    'host': 'test.rebex.net',
    'port': 21,
    'username': 'demo',
    'password': 'password',
    'remote_path': '/pub/' 
}

def enviar_datos_a_api(csv_file):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            payload = {
                "ClienteID": int(row["ClienteID"]),
                "Duracion": int(row["Duracion"]),
                "Resultado": row["Resultado"]
            }
            try:
                response = requests.post(API_URL, json=payload)
                response.raise_for_status()
                print(f"[✓] Enviado a API: {json.dumps(payload)}")
            except requests.exceptions.RequestException as e:
                print(f"[✗] Error al enviar: {payload} → {e}")

def subir_a_servidor(csv_file, config):
    if not os.path.isfile(csv_file):
        print(f"[✗] Archivo local no encontrado: {csv_file}")
        return

    try:
        import paramiko

        transport = paramiko.Transport((config['host'], 22))  # SFTP usa puerto 22
        transport.connect(username=config['username'], password=config['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.chdir('/pub/incoming')  # ✅ Cambiado a carpeta con permisos
        filename = os.path.basename(csv_file)
        sftp.put(csv_file, filename)

        print(f"[✓] Archivo subido vía SFTP a: /pub/incoming/{filename}")

        sftp.close()
        transport.close()
    except Exception as e:
        print(f"[✗] Error al subir por SFTP: {e}")


if __name__ == '__main__':
    print("📤 Enviando registros a API...")
    enviar_datos_a_api(CSV_FILE)

    print("\n📡 Subiendo CSV por SFTP...")
    subir_a_servidor(CSV_FILE, FTP_CONFIG)
    
    print("Proceso completado")

