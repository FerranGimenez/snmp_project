import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def snmpbulkwalk(version, rocommunity, agent, mib, oid):
    snmpEngine = SnmpEngine()

    objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData(rocommunity, mpModel=version),
            await UdpTransportTarget.create((agent, 161)),
            ContextData(),
            0,
            1,
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode = False
        )

    varBindsArray = []

    async for errorIndication, errorStatus, errorIndex, varBinds in objects:
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex}")
            break
        
        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
                varBindsArray.append(tuple(x.prettyPrint() for x in varBind))

    snmpEngine.close_dispatcher()
    return varBindsArray