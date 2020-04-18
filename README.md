# HELLOHERO!

Esta es una aplicacion basica para calcular impuestos, haciendo uso de una api de python en flask y html y javascript basico.
Para python version 3.8

# Librerias para instalar, windows
-flask
-requests
-pyodbc
-jwt

# Como instalar
pip install -r requirements.txt

## Crear archivo config.ini 
[APP]
ENVIRONMENT = development
DEBUG = False

[DATABASE]
USERNAME:usuario_bd
PASSWORD:password_bd
HOST:dominio_base_datos
DB: nombre_base_datos
[KEY]
SECRET=clave_secreta_api
