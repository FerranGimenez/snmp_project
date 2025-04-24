from flask import Flask, request, render_template
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

app = Flask(__name__)

@app.route('/endpoint00', methods=['GET', 'POST'])
def snmp_form():
    if request.method == 'POST':
        version = request.form['version']
        community = request.form['rocommunity']
        agent = request.form['agent']
        oid = request.form['oid']

        result = consultar_snmp(version, community, agent, oid)
        return render_template('result.html', resultado=result)

    return render_template('index.html')

def consultar_snmp(version, community, agent, oid):
    mp_model = 0 if version == '1' else 1  # 0 for SNMPv1, 1 for SNMPv2c

    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=mp_model),
        UdpTransportTarget((agent, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        return f"Error: {errorIndication}"
    elif errorStatus:
        return f"SNMP Error: {errorStatus.prettyPrint()}"
    else:
        return [f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds]

if __name__ == '__main__':
    app.run(debug=True)
