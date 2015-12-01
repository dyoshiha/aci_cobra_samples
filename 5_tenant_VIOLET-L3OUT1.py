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

#### Connect to APIC #####
moDir = EstablishConnection()
polUni = cobra.model.pol.Uni('')

### the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')
fvTenant = cobra.model.fv.Tenant(polUni, 'VIOLET')

### build the request using cobra syntax
# 1-1. Create and name L3OUT
l3extOut = cobra.model.l3ext.Out(fvTenant, name=u'VIOLET_L3OUT')
l3extRsEctx = cobra.model.l3ext.RsEctx(l3extOut, tnFvCtxName=u'VIOLET_VRF')

# 1-1-1. Specify the node which is connected to the external router
l3extLNodeP = cobra.model.l3ext.LNodeP(l3extOut, name=u'VIOLET_L3_BLEAF_102')
l3extRsNodeL3OutAtt = cobra.model.l3ext.RsNodeL3OutAtt(l3extLNodeP, tDn=u'topology/pod-1/node-102', rtrId=u'1.1.1.102')

# 1-1-2. Specify the interface which is connected to the external router on the node
l3extLIfP = cobra.model.l3ext.LIfP(l3extLNodeP, name=u'VIOLET_SUBI_BLEAF_102')
l3extRsPathL3OutAtt = cobra.model.l3ext.RsPathL3OutAtt(l3extLIfP, addr=u'192.168.95.2/24', mac=u'00:22:BD:F8:19:FF', encap=u'vlan-695', ifInstT=u'sub-interface', tDn=u'topology/pod-1/paths-102/pathep-[eth1/1]')

# 1-1-3. Configure an ospf related setting on the interface
ospfIfPol = cobra.model.ospf.IfPol(fvTenant, nwT=u'p2p', name=u'VIOLET_OSPFInterfacePolicy')
ospfIfP = cobra.model.ospf.IfP(l3extLIfP)
ospfRsIfPol = cobra.model.ospf.RsIfPol(ospfIfP, tnOspfIfPolName=u'VIOLET_OSPFInterfacePolicy')

# 1-2. Create and name L3 EPG
l3extInstP = cobra.model.l3ext.InstP(l3extOut, name=u'VIOLET_L3EPG')

# 1-2-1. Specify an import subnet
l3extSubnet = cobra.model.l3ext.Subnet(l3extInstP, ip=u'0.0.0.0/0', aggregate=u'')

# 1-3. Configure an ospf related setting
ospfExtP = cobra.model.ospf.ExtP(l3extOut, areaId=u'0.0.0.1')

# 1-4-1. Create contract
vzBrCP = cobra.model.vz.BrCP(fvTenant, name=u'VIOLET_CON_L3OUT')
vzSubj = cobra.model.vz.Subj(vzBrCP, name=u'VIOLET_Subject')
vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName=u'icmp')

# 1-4-2. Associate provided contract to the L3EPG
fvAp = cobra.model.fv.Ap(fvTenant, name='VIOLET_AP')
fvAEPg1 = cobra.model.fv.AEPg(fvAp, name='VIOLET_EPG_WEB_PHY')
fvRsProv = cobra.model.fv.RsProv(fvAEPg1, tnVzBrCPName=u'VIOLET_CON_L3OUT')

# 1-4-3. Associate consumed contract to the L3EPG
fvRsCons = cobra.model.fv.RsCons(l3extInstP, tnVzBrCPName=u'VIOLET_CON_L3OUT')

# 1-5. Configure the BD scope to 'public' and associate it to the L3OUT 
fvBD = cobra.model.fv.BD(fvTenant, 'VIOLET_BD_WEB_PHY')
fvSubnet = cobra.model.fv.Subnet(fvBD, ip='192.168.1.254/24', scope=u'public')
fvRsBDToOut = cobra.model.fv.RsBDToOut(fvBD, tnL3extOutName=u'VIOLET_L3OUT')

### Debug JSON Configuration
#print toJSONStr(topMo)

### Committing a Configuration
CommitChange(fvTenant)

