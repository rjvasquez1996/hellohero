#importamos flask para uso de la api
from flask import Flask, request, make_response,render_template, jsonify
import requests as req
#importamos pyodbc para conectar con sqlserver
import pymssql 
#importamos config para la configuracion de accesos
import config
#importamos jwt para la seguridad de los tokens
import jwt
#importamos datetime para el manejo de timempo
import datetime
#import wraps para manejo del auth y decorativos
from functools import wraps
import json as json
#importamos las librerias propia para funciones
from funciones import func
HEADERS_NEEDED=["id","nombre","descripcion","precio","cantidad","codigo_impuesto"]
HEADERS_DICT={"id":"int","nombre":"string","descripcion":"string","precio":"float","cantidad":"int","codigo_impuesto":"string"}
#creamos la conexion de la bd
msdb = pymssql.connect(server=config.HOST,user=config.USER,password=config.PASS, database=config.DATABASE)
conn=msdb.cursor()
#generamos la app para la api
app = Flask(__name__)
#verificamos el token para cada transaccion
def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.args.get("token")
        if not token:#si no existe el token
            return render_template("home.html")
        try:
            data = jwt.decode(token, config.SECRET_KEY)
        except:
            return jsonify({"status":False,"message":"Token es invalido","data":""}), 403
        return f(*args,**kwargs)
    return wrap

#definimos la ruta home
@app.route('/', methods=["GET"])
def home():
    return render_template("home.html")
#obtengo la pagina para calcular el token
@app.route('/calcular', methods=["GET"])
@token_required
def calculo():
    return render_template("calculo.html")

#ingresa a la bd nuestros datos nuevos ademas sube nuestro excel a s3
@app.route('/excel', methods=["POST"])
@token_required
def subir_excel():
    #obtengo dato del token
    token = request.args.get("token")
    #encripto con la secret key
    data=jwt.decode(token,config.SECRET_KEY)
    #obtengo la data del token
    id=data["user"]
    #obtengo la data del json
    try:
        jsondata=request.get_json()
    except:
        return jsonify({"status":False,"message":"error intentando obtener data del archivo","data":""})
    #verifico que cumpla con los headers
    if(func.check_headers(HEADERS_DICT,HEADERS_NEEDED,jsondata)==False):
        return jsonify({"status":False,"message":"El archivo no cumple con los datos necesarios","data":""})
    #subo la data en la bd
    fallidas=func.data_upload(conn,jsondata,id)
    #obtengo la data calculada
    jsondata=func.get_products(conn)
    #llamo a la api de s3
    APIawsURL="https://kkv35vo1u8.execute-api.us-east-1.amazonaws.com/dev/generar"
    HEADERS = {
        'Content-Type': 'application/json'
    }
    #uso metodo post
    res = req.post(APIawsURL,json=jsondata,auth=auth,headers=HEADERS)
    response =res.json()['data']
    #retorno data
    return jsonify({"status":True,"message":"json obtenido correctamente","data":response})
#defino mi ruta usuario
@app.route("/usuario",methods=["GET","PUT"])
@token_required
def usuarios():
    if(request.method=="GET"):
        #obtengo mi lista de usuarios
        usuarios=func.get_users(conn)
        return jsonify({"status":True,"message":"usuarios obtenidos correctamente ","data":usuarios})
    elif (request.method=="PUT"):
        try:
            jsondata=request.get_json()
            print(jsondata)
        except:
            return jsonify({"status":False,"message":"error intentando obtener data del usuario","data":""})
        if(jsondata.get("usuario") is None or jsondata.get("password") is None):
            return jsonify({"status":False,"message":"error debe ingresar usuario y password de manera correcta","data":""})
        func.add_user(conn,jsondata)
        return jsonify({"status":True,"message":"usuarios agregados correctamente","data":""})

#defino mi ruta impuestos
@app.route("/impuestos",methods=["GET"])
@token_required
def get_impuestos():
    #obtengo mi lista de impuestos
    impuestos=func.get_taxes(conn)
    return jsonify({"status":True,"message":"impuestos obtenidos correctamente ","data":impuestos})

#mi ruta login para loguearse
@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if(auth is None):
        return jsonify({"status":False,"message":"Se requiere login","data":""})
    query="select id from USUARIO where usuario=? and contraseña=CONVERT(VARCHAR(32),HashBytes('MD5','"+auth.password+"'),2)"
    cursor= conn.execute(query,auth.username) 
    res = cursor.fetchone()
    print(res)
    if(res is None):
        return jsonify({"status":False,"message":"Login ingresado es invalido","data":""})
        
    else:
        token = jwt.encode({"user":res[0],"exp":datetime.datetime.utcnow()+datetime.timedelta(days=1)},config.SECRET_KEY)
        return jsonify({"status":True,"message":"Login completado correctamente","data":token.decode('UTF-8')})
    return jsonify({"status":False,"message":"No se pudo verificar","data":""})
    

if __name__ == '__main__':
     app.run(port='5002',debug=False)