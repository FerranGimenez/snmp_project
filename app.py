from flask import Flask, render_template
from flask import request

app=Flask(__name__)

@app.route("/endpoint00", methods=['POST'])

def endpoint00():
    nombre=request.form.get("nombreusuari", type=str)
    edad=request.form.get("edadusuari", type=int)
    return render_template("tobuilddd.html",nombreusuari=nombre,edadusuari=edad)
