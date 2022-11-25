import datetime
import re

import requests as requests
from flask import Flask
from flask import jsonify #para que funciona
from flask import request
from flask_cors import CORS
import json
from waitress import serve

app=Flask(__name__)
cors = CORS(app)
#elementos para utilizar y crear token
from flask_jwt_extended import create_access_token
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#Esta es la clave que usara JWT para cifrar
app.config["JWT_SECRET_KEY"] = "apigateway"
jwt= JWTManager(app)


#Obtencion de datos y verificación de datos--------------------------------------------------------------------------------
@app.route("/login", methods=["POST"])#resivmos datos por eso usamos post
def autentificacion():
    datos = request.get_json() #enviamos formulario y que ibtenga los datos de este
    urlBack = configData["url-backend-seguridad"]+'/usuarios/validar' #Invocamos la url para la autetificacion
    cabeceras = {"Content-Type": "application/json; charset=uft-8"} #
    rta = requests.post(urlBack, json=datos, headers=cabeceras) #utilizamos el request con el metodo puesto antes
    if rta.status_code == 200:
        usr = rta.json()
        #Creacion de token
        vida_token= datetime.timedelta(seconds=60*60*24)#segundos-minutos-dias(60 seg por 60 min es igual a una hora y una hora por 24 es igual a un dia(Logica al dar tiempo))
        token= create_access_token(identity=usr, expires_delta=vida_token)
        return jsonify({"token": token, "usr_id":usr["id"]})
    else:
        return jsonify({"Mensaje": "Usuario o clave incorrectos"}), 401

#Aca lo que hacemos es ver si tiene o no permisos para la accion que quiere realizar----------------------------------------------
@app.before_request #esta anoctacion hace que antes del requests vamos a ejecutar algo
def before_request_callback():
    endPoint = limpiarPath(request.path) #se define a donde se dirije y utilizamos el limpiarpath declarado mas adelante para que el metodo se entienda
    rutas_excluidas = ["/login"]# aca lo que hacemos es exclir las rutas que no necesitamos que se validen
    if rutas_excluidas.__contains__(endPoint):# y aca decimos si la ruta excluida es el endpoint siga de largo de lo contrario
        pass
    elif verify_jwt_in_request():
        usr = get_jwt_identity()
        if usr["rol"] is not None:
            tieneAcceso = validarAcceso(usr["rol"]["id"], endPoint, request.method)
            if not tieneAcceso:
                return jsonify({"mensaje": "Permiso denegado"}), 401
            else:
                return jsonify({"Mensaje": "Permiso denegado"}), 401

#-----------------------------------------------------------------------------------------------------------------------
#Microservicios de Candidatos-------------------------------------------------------------------------------------------
#Obtener
@app.route("/candidatos",methods=['GET'])
def getCandidatos():
    print("Micro Servicio de Listar todos los estudiantes")
    urlBack = configData["url-backend-transaccional"]+'/candidatos'#elementos genericos que deberan tener cad microsercicio
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    rta = requests.get(urlBack, headers = cabeceras)
    json = rta.json()
    return jsonify(json)


#Crear
@app.route("/candidatos",methods=['POST'])
def postCandidatos(id_cedula,Numero_resolucion, Nombre, Apellido):
    urlBack = configData["url-backend-transaccional"] + '/candidatos'
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    body = {
        "id_cedula": id_cedula,
        "Numero_resolucion": Numero_resolucion,
        "Nombre": Nombre,
        "Apellido": Apellido
    }
    rta = requests.get(urlBack, json=body, headers=cabeceras)
    json = rta.json()
    return jsonify(json)


#Borrar
@app.route("/candidatos/<string:id_cedula>", methods=['DELETE'])
def deleteCandidato(id_cedula):
    urlBack = configData["url-backend-transaccional"] + '/candidatos/<string:cedula>'
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    rta = requests.get(urlBack, headers=cabeceras)
    json = rta.json()
    return jsonify(json)


#Actualizar
@app.route("/candidatos/<string:cedula>", methods=['PUT'])
def updateCandidato(id_cedula,Numero_resolucion, Nombre, Apellido):
    urlBack = configData["url-backend-transaccional"] + '/candidatos/<string:cedula>'
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    body = {
        "id_cedula": id_cedula,
        "Numero_resolucion": Numero_resolucion,
        "Nombre": Nombre,
        "Apellido": Apellido
    }
    rta = requests.get(urlBack, json=body, headers=cabeceras)
    json = rta.json()
    return jsonify(json)


#Obtener Por id
@app.route("/candidatos/<string:cedula>", methods=['GET'])
def getCandidato(cedula):
    urlBack = configData["url-backend-transaccional"] + '/candidatos/<string:cedula>'
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    rta = requests.get(urlBack, headers=cabeceras)
    json = rta.json()
    return jsonify(json)


#Microservicios de Candidatos-------------------------------------------------------------------------------------------
#Obtener





#Toca colocar los 20 microservicos para validacion y en algunos debemos enviar un json como en validaracceso





def validarAcceso(id_rol, url, metodo):
    urlBack = configData["url-backend-seguridad"]+'PermisosRol/"validar-permiso/rol/' + str(id_rol)
    cabeceras = {"Content-Type": "application/json; charset=uft-8"}
    body = {
        "url":url,
        "metodo":metodo
    }
    rts = request.get(urlBack, json=body, headers=cabeceras)
    acceso = False
    datos = rts.json()
    if("id" in datos):
        acceso = True
    return acceso



# Remplazar y limpiar los id por ? para poder realizar bien el trabajo del API--------------------------------------------------------
def limpiarPath(url):
    secciones = url.split("/") #este metodo hace que al recibir la url o lo que le enviemos lo divida entre el caracter que le coloquemos
    for seccion in secciones:
        if re.search('\\d', seccion): #re.search busca entre la url un caracter alfa numerico (\\d) y
            url = url.replace(seccion, "?")#replace lo remplaza por lo que nosotros le digamos (?)
    return url





#---------------------------------------------------------------------------------------------------------------------------------------


@app.route("/",methods=['GET'])
def msPrueba():
    json = {}
    json["message"] = "Mi primer micro servico con Flask en el API Gateway"
    return jsonify(json)



def cargueConfigFile():
    with open('config.json') as file:
        datos = json.load(file)
    return datos


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('API Gateway Ciclo 4 Mision TIC 2022 Grupo 32')
    configData = cargueConfigFile()
    print("Servidor Ejecutandose ..... en http//:"+configData["url-backend"]+":"+str(configData["port"]))
    serve(app, host=configData["url-backend"], port=configData["port"])


