#!/usr/bin/env python

'''
Created by Daisuke Yoshihara (dyoshiha@cisco.com) 

apic.py must be created in the same directory with the following lines:
URL = 'https://(apic IP address)
Login = '(userid)'
Password = '(password)'

'''
import cobra.mit
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model
import cobra.model.pol
import cobra.model.fv
import cobra.model.l3ext
import cobra.model.ip
import cobra.model.fvns
import cobra.model.infra
from cobra.model.vmm import ProvP, DomP, UsrAccP, CtrlrP, RsAcc
import datetime
from time import sleep
from cobra.internal.codec.jsoncodec import toJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr
import apic

# Import credentials from apic.py
URL = apic.URL
LOGIN = apic.Login
PASSWORD = apic.Password

def EstablishConnection():
    # Establish connection to APIC Controller
    loginSession = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD, timeout=300)
    moDir = cobra.mit.access.MoDirectory(loginSession)
    moDir.login()
    return moDir

def CommitChange(topMo):
    # Push confiugrations to APIC
    cfgRequest = cobra.mit.request.ConfigRequest()
    cfgRequest.addMo(topMo)
    result = moDir.commit(cfgRequest)
    if '200' in str(result):
        print '\nSuccess.\n######\n'

# Log
print '\nSending...\n'

# Connect to APIC
moDir = EstablishConnection()
moDir.login()

# the top level object on which operations will be made
uniMo = moDir.lookupByDn('uni')


#A1. Define Tenant 
fvTenant = cobra.model.fv.Tenant(uniMo, name='VIOLET')

#A2. Define Context
fvCtx = cobra.model.fv.Ctx(fvTenant, name='VIOLET_VRF')

#A3-1. Define Bridge Domian for EPG
fvBD1 = cobra.model.fv.BD(fvTenant, name='VIOLET_BD_WEB_PHY', arpFlood='yes')
fvBD2 = cobra.model.fv.BD(fvTenant, name='VIOLET_BD_APP_PHY', arpFlood='yes')

#A3-2. Associate BD to Context
cobra.model.fv.RsCtx(fvBD1, tnFvCtxName='VIOLET_VRF')
cobra.model.fv.RsCtx(fvBD2, tnFvCtxName='VIOLET_VRF')

#A4. Create Subnet (Define SVI for DB for EPG)
fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip='192.168.1.254/24')
fvSubnet2 = cobra.model.fv.Subnet(fvBD2, ip='192.168.2.254/24')

#A5. Create ANP
fvAp = cobra.model.fv.Ap(fvTenant, name='VIOLET_AP')

#A6-1. Create EPG
fvAEPg1 = cobra.model.fv.AEPg(fvAp, name='VIOLET_EPG_WEB_PHY')
fvAEPg2 = cobra.model.fv.AEPg(fvAp, name='VIOLET_EPG_APP_PHY')

#A6-2. Associate BD with EPG
cobra.model.fv.RsBd(fvAEPg1, tnFvBDName='VIOLET_BD_WEB_PHY')
cobra.model.fv.RsBd(fvAEPg2, tnFvBDName='VIOLET_BD_APP_PHY')

#A7-1. Create a Contract
vzBrCP = cobra.model.vz.BrCP(fvTenant, name='VIOLET_CON1_WEB_APP')

#A7-2. Consume a Contract from the EPG
fvRsCons = cobra.model.fv.RsCons(fvAEPg1, tnVzBrCPName='VIOLET_CON1_WEB_APP')

#A7-3. Provide a Contract from the EPG
fvRsProv = cobra.model.fv.RsProv(fvAEPg2, tnVzBrCPName='VIOLET_CON1_WEB_APP')

#A7-4. Create a Subject for the Contract
vzSubj = cobra.model.vz.Subj(vzBrCP, revFltPorts='yes', name='VIOLET_CON1_WEB_APP')

#A7-5. Create Filters for the Subject
vzFilter = cobra.model.vz.Filter(fvTenant, ownerKey='', name='VIOLET_Filter', descr='', ownerTag='')

#A7-6. Create Entries for the Filter 
vzEntry = cobra.model.vz.Entry(vzFilter, tcpRules='', arpOpc='unspecified', applyToFrag='no', dToPort='65535', descr='', prot='tcp', icmpv4T='unspecified', sFromPort='1', stateful='no', icmpv6T='unspecified', sToPort='65535', etherT='ip', dFromPort='1', name='TCP')
vzEntry2 = cobra.model.vz.Entry(vzFilter, tcpRules='', arpOpc='unspecified', applyToFrag='no', dToPort='unspecified', descr='', prot='icmp', icmpv4T='unspecified', sFromPort='unspecified', stateful='no', icmpv6T='unspecified', sToPort='unspecified', etherT='ip', dFromPort='unspecified', name='ICMP')

#A7-7. Define Provided Contract of EPG
vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName='VIOLET_Filter')

#A8-1. Associate Physical Domain with EPG
cobra.model.fv.RsDomAtt(fvAEPg1, tDn='uni/phys-static_phys', instrImedcy='immediate', resImedcy='immediate')
cobra.model.fv.RsDomAtt(fvAEPg2, tDn='uni/phys-static_phys', instrImedcy='immediate', resImedcy='immediate')

#A8-2. Static Binding
cobra.model.fv.RsPathAtt(fvAEPg1, instrImedcy='immediate', tDn='topology/pod-1/paths-201/pathep-[eth1/26]', encap='vlan-601')
cobra.model.fv.RsPathAtt(fvAEPg2, instrImedcy='immediate', tDn='topology/pod-1/paths-202/pathep-[eth1/26]', encap='vlan-602')

# Debug JSON Configuration
##print toJSONStr(topMo)

# Committing a Configuration
CommitChange(uniMo)

