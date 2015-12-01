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
from cobra.model.infra import RsVlanNs
from cobra.model.fvns import VlanInstP, EncapBlk
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

## Log
print '\nSending...\n'

#### Connect to APIC #####
moDir = EstablishConnection()
polUni = cobra.model.pol.Uni('')


##### B0-1. Create VMM #####
### Set the MO location
vmmProvP = cobra.model.vmm.ProvP(polUni, 'VMware')

### build the request using cobra syntax
# B0-1-1. Name VMM domain
vmmDomP = cobra.model.vmm.DomP(vmmProvP, name=u'SHARED_VMM_DOMAIN')

# B0-1-2. Create VMM domain components - VMM controller's credential
vmmUsrAccP = cobra.model.vmm.UsrAccP(vmmDomP, name=u'SHARED_CRE', pwd=u'vmware', usr=u'root')

# B0-1-3. Create VMM domain components - VMM controller's info
vmmCtrlrP = cobra.model.vmm.CtrlrP(vmmDomP, name=u'SHARED_VC', rootContName=u'DataCenter1', hostOrIp=u'10.71.129.110')
vmmRsAcc = cobra.model.vmm.RsAcc(vmmCtrlrP, tDn=u'uni/vmmp-VMware/dom-SHARED_VMM_DOMAIN/usracc-SHARED_CRE')

# B0-1-4. Associate VLAN pool to the VMM domain
infraRsVlanNs = cobra.model.infra.RsVlanNs(vmmDomP, tDn=u'uni/infra/vlanns-[SHARED_VP_VM]-dynamic')


### Committing a Configuration
CommitChange(vmmProvP)


