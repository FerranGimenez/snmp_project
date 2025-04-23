import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def snmpget(version, rocommunity, agent, mib, oid):
    snmpEngine = SnmpEngine()

    iterator = get_cmd(
        snmpEngine,
        CommunityData(rocommunity, mpModel=version),
        await UdpTransportTarget.create((agent, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
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