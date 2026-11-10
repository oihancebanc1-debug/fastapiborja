@echo off
chcp 65001 >nul
title API de Tareas
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 goto sinpython

if exist ".venv\Scripts\python.exe" goto instalar
echo [1/3] Creando entorno virtual (solo la primera vez)...
python -m venv .venv
if errorlevel 1 goto error

:instalar
echo [2/3] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto error

if exist ".env" goto arrancar
echo.
echo Para que tus companeros vean la API necesitas tu token de ngrok:
echo   https://dashboard.ngrok.com/get-started/your-authtoken
echo.
set "TOKEN="
set /p "TOKEN=Pega el token y pulsa Enter (o solo Enter para usarla en local): "
> .env echo NGROK_AUTHTOKEN=%TOKEN%
>> .env echo PUERTO=8000

:arrancar
echo [3/3] Arrancando la API...
echo.
".venv\Scripts\python.exe" run.py
pause
exit /b

:sinpython
echo No encuentro Python. Instalalo desde https://www.python.org/downloads/
echo y marca la casilla "Add python.exe to PATH" durante la instalacion.
pause
exit /b

:error
echo.
echo Algo ha fallado. Haz una captura de esta ventana y mandasela a Claude.
pause
