from flask import Flask, request, render_template
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor()

@app.route('/endpoint00', methods=['GET', 'POST'])
def snmp_form():
    if request.method == 'POST':
        version     = request.form['version']       
        comunidad   = request.form['rocommunity']   
        agente      = request.form['agent']         
        oid         = request.form['oid']           
        operacion   = request.form['operacion']     
        nuevo_valor = request.form.get('new_value') 

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resultado = loop.run_until_complete(
            dispatch_snmp_async(version, comunidad, agente, oid, operacion, nuevo_valor)
        )
        loop.close()

        return render_template('result.html', resultado=resultado)

    return render_template('index.html')


async def dispatch_snmp_async(version, comunidad, agente, oid, operacion, nuevo_valor=None):
    mp_model = 0 if version == '1' else 1
    # añadir ".0"
    if operacion in ('GET', 'NEXT', 'SET') and not oid.strip().endswith('.0'):
        oid += '.0'

    if operacion == 'GET':
        return await snmp_get(mp_model, comunidad, agente, oid)
    elif operacion == 'NEXT':
        return await snmp_next(mp_model, comunidad, agente, oid)
    elif operacion == 'BULKWALK':
        return await snmp_bulk_walk(mp_model, comunidad, agente, oid)
    elif operacion == 'SET':
        return await snmp_set(mp_model, comunidad, agente, oid, nuevo_valor)
    else:
        return [f"Operación desconocida: {operacion}"]


async def snmp_get(mp_model, comunidad, agente, oid):
    snmpEngine = SnmpEngine()
    iterator = get_cmd(
        snmpEngine,
        CommunityData(comunidad, mpModel=mp_model),
        await UdpTransportTarget.create((agente, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errInd, errStatus, errIndex, varBinds = await iterator
    snmpEngine.close_dispatcher()

    if errInd:
        return [f"Error: {errInd}"]
    if errStatus:
        return [f"SNMP Error: {errStatus.prettyPrint()}"]
    return [f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds]




async def snmp_next(mp_model, comunidad, agente, oid):
    snmpEngine = SnmpEngine()
    iterator = next_cmd(
        snmpEngine,
        CommunityData(comunidad, mpModel=mp_model),
        await UdpTransportTarget.create((agente, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errInd, errStatus, errIndex, varBinds = await iterator
    snmpEngine.close_dispatcher()

    if errInd:
        return [f"Error: {errInd}"]
    if errStatus:
        return [f"SNMP Error: {errStatus.prettyPrint()}"]
    return [f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds]

async def snmp_bulk_walk(mp_model, comunidad, agente, oid):
    snmpEngine = SnmpEngine()
    iterator = bulk_walk_cmd(
        snmpEngine,
        CommunityData(comunidad, mpModel=mp_model),
        await UdpTransportTarget.create((agente, 161)),
        ContextData(),
        0,               
        1,               
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
    resultados = []
    async for errInd, errStatus, errIndex, varBinds in iterator:
        if errInd:
            resultados.append(f"Error: {errInd}")
            break
        if errStatus:
            resultados.append(f"SNMP Error: {errStatus.prettyPrint()}")
            break
        for vb in varBinds:
            resultados.append(" = ".join([x.prettyPrint() for x in vb]))

    snmpEngine.close_dispatcher()
    return resultados


async def snmp_set(mp_model, comunidad, agente, oid, nuevo_valor):
    snmpEngine = SnmpEngine()
    if isinstance(nuevo_valor, bool):
        nuevo_valor = 1 if nuevo_valor else 0
    if isinstance(nuevo_valor, str):
        obj = ObjectType(ObjectIdentity(oid), OctetString(nuevo_valor))
    else:
        try:
            nuevo_int = int(nuevo_valor)
            obj = ObjectType(ObjectIdentity(oid), Integer(nuevo_int))
        except:
            return [f"Valor para SET inválido: {nuevo_valor}"]

    iterator = set_cmd(
        snmpEngine,
        CommunityData(comunidad, mpModel=mp_model),
        await UdpTransportTarget.create((agente, 161)),
        ContextData(),
        obj
    )
    errInd, errStatus, errIndex, varBinds = await iterator
    snmpEngine.close_dispatcher()

    if errInd:
        return [f"Error: {errInd}"]
    if errStatus:
        return [f"SNMP Error: {errStatus.prettyPrint()}"]
    return [f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds]


if __name__ == '__main__':
    app.run(debug=True)
