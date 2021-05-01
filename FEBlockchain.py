# Libreria de FASK sive para
import os
from flask import Flask, render_template, request, abort, jsonify
from werkzeug.utils import secure_filename

from lxml import etree
from xml.etree.ElementTree import ElementTree

import hashlib
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import pymongo


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './FacturasElectronicas'


@app.route("/")
def upload_file():
    return render_template('formulario.html')


@app.route("/upload", methods=['POST'])
def uploader():
    if request.method == 'POST':

        f = request.files['archivo']
        doc = etree.parse(f)
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        NumFactura = doc.findtext("fac/numfactura")
        CUFE = doc.findtext("fac/CUFE")
        FechaCreacion = doc.findtext("fac/startdate")
        NIT = doc.findtext("fac/nitempresa")
        ValorFactura = doc.findtext("fac/totalvalor")

        #Conexion a la base de datos "Blockchain" y seleccion de la coleccion "Bloques"
        client = MongoClient('localhost', port=27017, username='', password='')
        db = client['Blockchain']
        col = db['Bloques']

        #Se guarda en la variable "colvacia" si la coleccion "Bloques" esta vacia
        colvacia = (col.count() == 0)
        
        #Si "colvacia" es "true" el HashAnterior es "Genesis" y el NumeroBloque es 1
        if(colvacia == True):
            HashAnterior = "Genesis"
            NumeroBloque = 1
            NumeroBloque = str(NumeroBloque)
            encri = hashlib.sha256(NumeroBloque.encode()+NumFactura.encode()+CUFE.encode()+FechaCreacion.encode()
                               + NIT.encode()+ValorFactura.encode()+HashAnterior.encode())
            HashActual = encri.hexdigest()
            #Se insertan los valores en la base de datos
            col.insert_one({'NumFactura': NumFactura, 'CUFE': CUFE, 'FechaCreacion': FechaCreacion, 'NIT': NIT,
                        'ValorFactura': ValorFactura, 'HashAnterior': HashAnterior, 'HashActual': HashActual, 'NumeroBloque': NumeroBloque
            })

        if (colvacia == False):
            #Se guarda en la variable "bloquecodificado" el ultimo bloque que se inserto
            bloquecodificado = col.find().sort('NumeroBloque', -1).limit(1)
            #se recorren los items dentro de ese ultimo bloque 
            #cada item se guarda en la variable "bloqueanterior"
            for item in bloquecodificado :
                bloqueanterior = item
            #Dentro de la lista que se guardo en "bloqueanterior" se selecciona el campo "NumeroBloque"
            numbloqant = bloqueanterior['NumeroBloque']
            #Dentro de la lista que se guardo en "bloqueanterior" se selecciona el campo "HashActual"
            hashbloqant = bloqueanterior['HashActual']
            numbloqant= int(numbloqant)
            NumeroBloque = numbloqant + 1
            HashAnterior = hashbloqant
            #Se convierten las variables en string para poderla guardar en la base de datos
            NumeroBloque = str(NumeroBloque)
            HashAnterior = str(HashAnterior)
            #Se encripta la informacion
            encri = hashlib.sha256(NumeroBloque.encode()+NumFactura.encode()+CUFE.encode()+FechaCreacion.encode()
                               + NIT.encode()+ValorFactura.encode()+HashAnterior.encode())
            HashActual = encri.hexdigest()
            #Se insertan los valores en la base de datos
            col.insert_one({'NumFactura': NumFactura, 'CUFE': CUFE, 'FechaCreacion': FechaCreacion, 'NIT': NIT,
                        'ValorFactura': ValorFactura, 'HashAnterior': HashAnterior, 'HashActual': HashActual, 'NumeroBloque': NumeroBloque
            })

        return render_template('formulario.html', NumFactura=NumFactura, CUFE=CUFE, FechaCreacion=FechaCreacion,
                    NIT=NIT, ValorFactura=ValorFactura, HashAnterior=HashAnterior, HashActual=HashActual, NumeroBloque=NumeroBloque)


        


@app.route("/mostrar", methods=['POST'])
#Luego de que activa el metodo 'POST' con la ruta "/mostrar" corre la siguiente funcion
def subirinfo():
    if request.method == 'POST':
        #Se conecta a la base de datos "Blockchain" y la coleccion "Bloques"
        client = MongoClient('localhost', port=27017, username='', password='')
        db = client['Blockchain']
        col = db['Bloques']
        #Se consulta los bloques creados y se guarda en la variable "listabloques"
        listabloques = col.find()
        

    return render_template('verbloques.html', listabloques=listabloques)



 

if __name__ == '__main__':
    app.run(debug=True)
