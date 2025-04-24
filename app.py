from flask import Flask, request, render_template
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor()

@app.route('/endpoint00', methods=['GET', 'POST'])
def snmp_form():
    if request.method == 'POST':
        version = request.form['version']
        community = request.form['rocommunity']
        agent = request.form['agent']
        oid = request.form['oid']

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(consultar_snmp_async(version, community, agent, oid))
        loop.close()

        return render_template('result.html', resultado=result)

    return render_template('index.html')

async def consultar_snmp_async(version, community, agent, oid):
    mp_model = 0 if version == '1' else 1

    snmpEngine = SnmpEngine()

    if '.' in oid:
        # Consulta simple (GET)
        iterator = get_cmd(
            snmpEngine,
            CommunityData(community, mpModel=mp_model),
            await UdpTransportTarget.create((agent, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        
        # Espera el resultado directamente
        errorIndication, errorStatus, errorIndex, varBinds = await iterator
    else:
        # Consulta múltiple (BULKWALK)
        iterator = bulk_walk_cmd(
            snmpEngine,
            CommunityData(community, mpModel=mp_model),
            await UdpTransportTarget.create((agent, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
        )

        # Itera sobre todos los resultados
        resultados = []
        while True:
            try:
                errorIndication, errorStatus, errorIndex, varBinds = await iterator
                if errorIndication:
                    return f"Error: {errorIndication}"
                elif errorStatus:
                    return f"SNMP Error: {errorStatus.prettyPrint()}"
                else:
                    for varBind in varBinds:
                        resultados.append(" = ".join([x.prettyPrint() for x in varBind]))
            except StopAsyncIteration:
                break

        return resultados

    if errorIndication:
        return f"Error: {errorIndication}"
    elif errorStatus:
        return f"SNMP Error: {errorStatus.prettyPrint()}"
    else:
        return [f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds]

if __name__ == '__main__':
    app.run(debug=True)