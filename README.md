# HELLOHERO!

Esta es una aplicacion basica para calcular impuestos, haciendo uso de una api de python en flask y html y javascript basico.
Para python version 3.8

# Librerias para instalar
-flask
**pip install flask**
-requests
**pip install requests**
-pyodbc
**pip install pyodbc**
-flask_jsonpify
**pip install flask_jsonpify**
-jwt
**pip install pyjwt**

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
