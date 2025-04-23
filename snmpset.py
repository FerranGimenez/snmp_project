import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def snmpset(version, rwcommunity, agent, mib, oid, new_value):
    snmpEngine = SnmpEngine()

    # SNMP Data Types 
    # https://docs.lextudio.com/snmp/snmp-design#data-types
    # https://stackoverflow.com/questions/59154328/pysnmp-unable-to-set-value-of-oid-str-object-has-no-attribute-gettagset

    if type(new_value) == bool:
        if new_value == True:
            new_value = 1
        else:
            new_value = 0
    
    ObjType = None

    if type(new_value) == str:
        ObjType = ObjectType(ObjectIdentity(oid), OctetString(new_value))
    elif type(new_value) == int:
        ObjType = ObjectType(ObjectIdentity(oid), Integer(new_value))

    iterator = set_cmd(
        snmpEngine,
        CommunityData(rwcommunity, mpModel=version),
        await UdpTransportTarget.create((agent, 161)),
        ContextData(),
        ObjType
    )    

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))

        snmpEngine.close_dispatcher()
        return varBinds

    snmpEngine.close_dispatcher()
    return None