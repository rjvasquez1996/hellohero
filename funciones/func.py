#funcion apra verificar que cumplen con los headers obligatorios
def check_headers(headers_dict,headers,json):
    #itera el json
    for data in json:
        #itera los headers
        for header in headers:
            #si no tiene ese header
            if(data.get(header) == None ):
                return False
            #si la data no hace match con el dict
            if(check_data(headers_dict,header,data)==False):
                return False
    return True
#verifica los headers segun el dict de headers
def check_data(headers_dict,header,data):
    #verifica el tipo de dato segun el dict
    if(headers_dict[header]=="int"):
        try:
            int(data[header])
        except:
            return False
    elif headers_dict[header]=="string":
        try:
            str(data[header])
        except:
            return False
    else :
        try:
            float(data[header])
        except:
            return False

    return True
#sube la informacion a la bd y a s3 y obtiene las compras fallidas
def data_upload(conn,cursor,jsondata,id,url):
    #verifica las claves de  impuestos ingresados
    queryverificacion="select clave from IMPUESTO "
    cursor.execute(queryverificacion)
    impuestos=cursor.fetchall()
    lista_impuesto=[]
    for imp in impuestos:
        lista_impuesto.append(imp[0])    
    #declaro compras fallidas
    compras_fallidas=[]
    #actualizo el url actual de las compras en la bd
    query="update S3_URL set url='"+url+"'"
    cursor.execute(query)
    #verifico si es insercion o actualizacion de datos
    for data in jsondata:
        if(data["codigo_impuesto"] not in lista_impuesto):
            compras_fallidas.append(data)
            continue
        query="""if not exists( select id from COMPRA where id="""+str(data["id"])+""")
                begin 
                    if not exists(select id from PRODUCTO where nombre='"""+str(data["nombre"])+"""')
                    begin
                        insert into PRODUCTO(clave,nombre) values((cast(ident_current('PRODUCTO') as varchar)+'-"""+data["nombre"][0:5]+"""'),'"""+data["nombre"]+"""')
                    end
                    insert into COMPRA (id,id_impuesto,id_producto,precio,descripcion,cantidad,subtotal,costo_impuesto,total,fecha_compra,creado_por)
                    values(
                        """+str(data["id"])+""",
                        (select id from IMPUESTO where clave='"""+str(data["codigo_impuesto"])+"""'),
                        (select id from PRODUCTO where nombre='"""+str(data["nombre"])+"""'),
                        cast('"""+str(data["precio"])+"""' as numeric(18,2)),
                        '"""+str(data["descripcion"])+"""',
                        """+str(data["cantidad"])+""",
                        (cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+"""),
                        (select valor*(cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+""")/100 from IMPUESTO where clave='"""+data["codigo_impuesto"]+"""'),
                        (select ((valor+100)/100)*(cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+""") from IMPUESTO where clave='"""+data["codigo_impuesto"]+"""'),
                        getdate(),
                        """+str(id)+"""
                        )
                end
                else
                begin
                    if not exists(select id from PRODUCTO where nombre='"""+str(data["nombre"])+"""')
                    begin
                        insert into PRODUCTO(clave,nombre) values((cast(ident_current('PRODUCTO') as varchar)+'-"""+data["nombre"][0:5]+"""'),'"""+data["nombre"]+"""')
                    end
                    update COMPRA 
                    set 
                    id_impuesto=(select id from IMPUESTO where clave='"""+str(data["codigo_impuesto"])+"""'),
                    id_producto=(select id from PRODUCTO where nombre='"""+str(data["nombre"])+"""'),
                    precio=cast('"""+str(data["precio"])+"""' as numeric(18,2)),
                    descripcion='"""+str(data["descripcion"])+"""',
                    cantidad="""+str(data["cantidad"])+""",
                    subtotal=(cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+"""),
                    costo_impuesto=(select valor*(cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+""")/100 from IMPUESTO where clave='"""+data["codigo_impuesto"]+"""'),
                    total=(select ((valor+100)/100)*(cast('"""+str(data["precio"])+"""' as numeric(18,2))*"""+str(data["cantidad"])+""") from IMPUESTO where clave='"""+data["codigo_impuesto"]+"""')                    
                    where id="""+data["id"]+"""
                end
                """
        cursor.execute(query)
    conn.commit()
    return compras_fallidas
def get_products(conn,cursor):
    query="""select compra.id, compra.precio, PRODUCTO.nombre, compra.descripcion, compra.cantidad, 
            imp.clave as codigo_impuesto, t_imp.nombre as nombre_impuesto, imp.valor as porcentaje_impuesto, 
            compra.subtotal, COMPRA.costo_impuesto, total, 
            convert(varchar(10),fecha_compra,126)+' '+convert(varchar(5),fecha_compra,108) fecha_compra 
            FROM COMPRA as compra JOIN IMPUESTO as imp on(compra.id_impuesto=imp.id)
            JOIN PRODUCTO on (PRODUCTO.id=COMPRA.id_producto) 
            JOIN TIPO_IMPUESTO as t_imp on (imp.id_tipo=t_imp.id) """
    cursor.execute(query) 
    res = cursor.fetchall()
    prod=[]
    for row in res:
        prod.append(
            {
                "id":str(row[0]), 
                "precio":str(row[1]),
                "nombre":str(row[2]), 
                "descripcion":str(row[3]),
                "cantidad":str(row[4]),
                "clave_impuesto":str(row[5]),
                "nombre_impuesto":str(row[6]),
                "porcentaje_impuesto":str(row[7]),
                "subtotal":str(row[8]),
                "costo_impuesto":str(row[9]),
                "total":str(row[10]),
                "fecha_compra":str(row[11]),
            })
    return prod

def get_url(cursor):
    query="""select [url] from S3_URL"""
    cursor.execute(query) # ejecuto el query
    res = cursor.fetchall()
    url=""
    for row in res:
        url=row[0]
    
    return url

def get_users(cursor):
    query="""select id,usuario from USUARIO order by id ASC"""
    cursor.execute(query) # ejecuto el query
    res = cursor.fetchall()
    usuarios=[]
    for row in res:
        usuarios.append(
            {
                "id":str(row[0]), 
                "usuario":str(row[1])
            })
    
    return usuarios


def add_user(conn,cursor,data):
    usuario=data["usuario"]
    password=data["password"]
    if(usuario is None or usuario==""):
        return False
    query="select id from usuario where usuario='"+usuario+"'"
    cursor.execute(query) # ejecuto el query
    res = cursor.fetchone()
    for row in res:
        return False
    query=" insert into USUARIO(usuario,contraseña) values('"+usuario+"',CONVERT(VARCHAR(32),HashBytes('MD5','"+password+"'),2))"
    cursor.execute(query)
    conn.commit()
    return True

def get_taxes(cursor):
    query="""select IMPUESTO.id,IMPUESTO.clave,IMPUESTO.valor from IMPUESTO  order by id ASC"""
    cursor.execute(query) 
    res = cursor.fetchall()
    impuestos=[]
    for row in res:
        impuestos.append(
            {
                "id":str(row[0]), 
                "clave":str(row[1]),
                "valor":str(row[2]),
            })
    return impuestos
