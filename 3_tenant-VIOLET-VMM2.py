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
	# Push confiugrations to ACI fabric
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


##### B0-1-5. Associate VMM domain to AEP #####
### Set the MO location
topMo = moDir.lookupByDn('/uni/infra/attentp-SHARED_AEP_VM')

### build the request using cobra syntax
infraRsDomP = cobra.model.infra.RsDomP(topMo, tDn='uni/vmmp-VMware/dom-SHARED_VMM_DOMAIN')

### Committing a Configuration
CommitChange(topMo)


