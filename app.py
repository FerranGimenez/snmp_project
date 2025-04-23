from flask import Flask, render_template
from flask import request

app=Flask(__name__)

@app.route("/endpoint0")

def endpoint0():
    return "Hola 2Asix, Estás en EndPoint0 ..."
#ejemplo con tag HTML -> return "<html><body><h2>Hola sossios</h2></body></html>"

@app.route("/endpoint1")

def endpoint1():
    return "Hola 2Asix, Estás en EndPoint1, para ir a EndPoint0, <h2>Pulsa <a href='/endpoint0'>Aquí</a></h2>"

@app.route("/endpoint2/<nombre>")

def endpoint2(nombre): #Devolver valor variable
    return f"<html><body><h2>Hola {nombre}. Estás en EndPoint2</h2></body></html>"

@app.route("/endpoint3")

def endpoint3(): #acceso a plantilla html en templates
    nombre="Paco"
    return render_template("endpoint3.html",usuari=nombre)

@app.route("/endpoint3bis/<nombre>")

def endpoint3bis(nombre): #acceso a plantilla html en templates
    return render_template("endpoint3.html",usuari=nombre)

@app.route("/endpoint4")

def endpoint4(): #acceso a plantilla html en templates
    nombre=request.args.get("nombre", default="anonimo", type=str)
    edad=request.args.get("edad", default="69", type=int)
    return render_template("endpoint4.html",nombreusuari=nombre,edadusuari=edad)

@app.route("/endpoint5")

def endpoint5():
    return render_template("endpoint5.html")

@app.route("/endpoint6", methods=['POST'])

def endpoint6():
    nombre=request.form.get("nombreusuari", type=str)
    edad=request.form.get("edadusuari", type=int)
    return render_template("endpoint4.html",nombreusuari=nombre,edadusuari=edad)