"""Arranca la API, abre la interfaz en el navegador y, si puede, la publica con ngrok.

Uso:  doble clic en INICIAR.bat   (o:  python run.py)
Si ngrok falla, la API funciona igual en local: http://127.0.0.1:8000
"""
import os
import tempfile
import threading
import webbrowser
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

CARPETA = Path(__file__).resolve().parent
os.chdir(CARPETA)
load_dotenv(CARPETA / ".env")

PUERTO = int(os.getenv("PUERTO", 8000))
TOKEN = (os.getenv("NGROK_AUTHTOKEN") or "").strip()
LOCAL = f"http://127.0.0.1:{PUERTO}"

# ngrok se descarga y guarda DENTRO del proyecto (no en la carpeta Temp de Windows,
# que es la que daba el error "Invalid argument").
TMP = CARPETA / ".tmp"
TMP.mkdir(exist_ok=True)
tempfile.tempdir = str(TMP)
NGROK_EXE = CARPETA / ("ngrok.exe" if os.name == "nt" else "ngrok")


def abrir_ngrok():
    """Devuelve la URL pública o None si no se pudo."""
    if not TOKEN or TOKEN == "pega_aqui_tu_token":
        print("[!] No hay token de ngrok en el archivo .env -> solo funcionara en local.")
        return None
    try:
        from pyngrok import conf, ngrok
        conf.get_default().ngrok_path = str(NGROK_EXE)
        conf.get_default().auth_token = TOKEN
        if not NGROK_EXE.exists():
            print("Descargando ngrok (solo la primera vez)...")
        return ngrok.connect(PUERTO, "http").public_url
    except Exception as e:
        print(f"[!] ngrok ha fallado: {e}")
        print("    Solucion: descarga ngrok de https://ngrok.com/download (Windows),")
        print(f"    descomprime y pon ngrok.exe en: {CARPETA}")
        print("    Mientras tanto la API funciona en local.")
        return None


url = abrir_ngrok()

print("\n" + "=" * 64)
print(f"  Interfaz en tu PC:   {LOCAL}")
if url:
    print(f"  Interfaz publica:    {url}   <- pasasela a tus companeros")
    print(f"  Documentacion API:   {url}/docs")
print("  Para parar: Ctrl+C (o cierra esta ventana)")
print("=" * 64 + "\n")

threading.Timer(2, lambda: webbrowser.open(LOCAL)).start()   # abre el navegador solo

try:
    uvicorn.run("main:app", host="0.0.0.0", port=PUERTO)
finally:
    if url:
        from pyngrok import ngrok
        ngrok.kill()
