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
#from netaddr import *
#from credentials import *
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

#### Connect to APIC #####
moDir = EstablishConnection()
polUni = cobra.model.pol.Uni('')

### Set the MO location
uniMo = moDir.lookupByDn('uni')

#B1. Define Tenant 
fvTenant = cobra.model.fv.Tenant(uniMo, name='VIOLET')

#B2. Define Context
fvCtx = cobra.model.fv.Ctx(fvTenant, name='VIOLET_VRF')

#B3-1. Define Bridge Domian
fvBD3 = cobra.model.fv.BD(fvTenant, name='VIOLET_BD_WEB_VM', arpFlood='yes')
fvBD4 = cobra.model.fv.BD(fvTenant, name='VIOLET_BD_APP_VM', arpFlood='yes')

#B3-2. Associate BD to Context
cobra.model.fv.RsCtx(fvBD3, tnFvCtxName='VIOLET_VRF')
cobra.model.fv.RsCtx(fvBD4, tnFvCtxName='VIOLET_VRF')

#B4. Create Subnet (Define SVI for DB for EPG)
fvSubnet3 = cobra.model.fv.Subnet(fvBD3, ip='192.168.41.254/24')
fvSubnet4 = cobra.model.fv.Subnet(fvBD4, ip='192.168.42.254/24')

#B5. Create ANP
fvAp = cobra.model.fv.Ap(fvTenant, name='VIOLET_AP')

#B6-1. Create EPG
fvAEPg3 = cobra.model.fv.AEPg(fvAp, name='VIOLET_EPG_WEB_VM')
fvAEPg4 = cobra.model.fv.AEPg(fvAp, name='VIOLET_EPG_APP_VM')

#B6-2. Associate BD with EPG
cobra.model.fv.RsBd(fvAEPg3, tnFvBDName='VIOLET_BD_WEB_VM')
cobra.model.fv.RsBd(fvAEPg4, tnFvBDName='VIOLET_BD_APP_VM')

#B7-1. Create a Contract
vzBrCP = cobra.model.vz.BrCP(fvTenant, name='VIOLET_CON2_WEB_APP')

#B7-2. Consume a Contract from the EPG
fvRsCons = cobra.model.fv.RsCons(fvAEPg3, tnVzBrCPName='VIOLET_CON2_WEB_APP')

#B7-3. Provide a Contract from the EPG
fvRsProv = cobra.model.fv.RsProv(fvAEPg4, tnVzBrCPName='VIOLET_CON2_WEB_APP')

#B7-4. Create a Subject for the Contract
vzSubj = cobra.model.vz.Subj(vzBrCP, revFltPorts='yes', name='VIOLET_CON2_WEB_APP')

#B7-5. Create Filters for the Subject
vzFilter = cobra.model.vz.Filter(fvTenant, ownerKey='', name='VIOLET_Filter2', descr='', ownerTag='')

#B7-6. Create Entries for the Filter
vzEntry = cobra.model.vz.Entry(vzFilter, tcpRules='', arpOpc='unspecified', applyToFrag='no', dToPort='65535', descr='', prot='tcp', icmpv4T='unspecified', sFromPort='1', stateful='no', icmpv6T='unspecified', sToPort='65535', etherT='ip', dFromPort='1', name='TCP')
vzEntry2 = cobra.model.vz.Entry(vzFilter, tcpRules='', arpOpc='unspecified', applyToFrag='no', dToPort='unspecified', descr='', prot='icmp', icmpv4T='unspecified', sFromPort='unspecified', stateful='no', icmpv6T='unspecified', sToPort='unspecified', etherT='ip', dFromPort='unspecified', name='ICMP')

#B7-7. Define Provided Contract of EPG
vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName='VIOLET_Filter2')

#B8-1. Associate VMM Domain with EPG
fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg3, tDn='uni/vmmp-VMware/dom-SHARED_VMM_DOMAIN', instrImedcy='immediate', resImedcy='immediate')
fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg4, tDn='uni/vmmp-VMware/dom-SHARED_VMM_DOMAIN', instrImedcy='immediate', resImedcy='immediate')

# Committing a Configuration
CommitChange(uniMo)


