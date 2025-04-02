###Replace PVWA_LB_HERE with your PVWA Load Balancer Name and run this script with admin account

import requests
import time
import getpass
import urllib3
import json
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
	username = input("Enter your vault username:")
	password = getpass.getpass("Enter vault password:")
except:
	print('ERROR', err)
	
f_usr = open("acc_passwd.csv","w")
f1 = open("CyberArk_account_details.csv","w")
f1.write("ACCOUNT_ID,TARGET,ACCOUNT_NAME,PLATFORM_NAME,SAFE_NAME,SERVERS\n")

url = "https://PVWA_LB_HERE/PasswordVault/WebServices/auth/CyberArk/CyberArkAuthenticationService.svc/Logon"

headers = { 'Content-Type': 'application/json','Cache-Control': 'max-age=300'}
data = '{ "username":"'+username+'","password":"'+password+'", "useRadiusAuthentication":"false", "connectionNumber":"1"}'
response = requests.request("POST",url, headers=headers, data=data, verify=False)
login_response = response.status_code
output_response = response.json()
auth_token = output_response['CyberArkLogonResult']
time.sleep(1)

if login_response == 200:
	print("Logon completed successfully with status_code: {}".format(login_response))
else:
	print("Logon failed with status_code: {}".format(login_response))
	sys.exit()
	
url_pvwa = "https://PVWA_LB_HERE/PasswordVault/"
url_acc = "api/Accounts?limit=1000"

While True:
	url_get_acc = url_pvwa + url_acc
	headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
	response = requests.get(url_get_acc, headers=headers, verify=False)
	login_response = response.status_code
	output_response = response.json()
	
	for j in output_response["value"]:
		existing_servers = ''
		if "SSHKeys" not in j["platformId"]:
			print("Processing to get password for %s user of %s target under %s safe and platform %s. Unique AccountID: %s" %(j["userName"],j["address"],j["safeName"],j["platformId"],j["id"]))
			url_get_passwd = "https://PVWA_LB_HERE/PasswordVault/api/Accounts/%s/Password/Retrieve" %j["id"]
			headers = { 'Content-Type': 'application/json', 'Connection': 'keep-alive', 'Authorization':auth_token}
			pass_data = '{reason:"backup"}'
			respo = requests.request("POST",url_get_passwd, data=pass_data, headers=headers, verify=False)
			time.sleep(1)
			statusCode = respo.status_code
			output_respo = respo.json()
			if "20" in str(statusCode):
				print("account password pulled successfully with status_code: {}".format(statusCode))
				f_usr.write("%s,%s,%s,%s,%s\n" %(j["address"],j["userName"],j["platformId"],j["safeName"],output_respo))
			else:
				print("Failed to get password with status_code: {}".format(statusCode))
				f_usr.write("%s,%s,%s,%s,FAILED_TO_GET_PASSWORD\n" %(j["address"],j["userName"],j["platformId"],j["safeName"]))
		else:
			print("Processing to get password for %s user of %s target under %s safe and platform %s. Unique AccountID: %s" %(j["userName"],j["address"],j["safeName"],j["platformId"],j["id"]))
			print("Account using ssh keys")
			f_usr.write("%s,%s,%s,%s,SSH_KEYS\n" %(j["address"],j["userName"],j["platformId"],j["safeName"]))
		if "remoteMachines" in str(j):
			existing_servers = j["remoteMachinesAccess"]["remoteMachines"]
			exi_ser = existing_servers.split(';')
			for m in range(0, len(exi_ser)):
				print(j["id"],j["address"],j["userName"],j["platformId"],j["safeName"],exi_ser[m])
				f1.write("%s,%s,%s,%s,%s,%s" %(j["id"],j["address"],j["userName"],j["platformId"],j["safeName"],exi_ser[m]))
		else:
			existing_servers = "'Servers not mentioned explicitly'"
			print(j["id"],j["address"],j["userName"],j["platformId"],j["safeName"],existing_servers)
			f1.write("%s,%s,%s,%s,%s,%s" %(j["id"],j["address"],j["userName"],j["platformId"],j["safeName"],existing_servers))
	if "nextLink" in output_response:
		print(output_response["nextLink"])
		url_acc = output_response["nextLink"]
	else:
		break
		
f_usr.close()
f1.close()

url = "https://PVWA_LB_HERE/PasswordVault/WebServices/auth/Shared/RestfulAuthenticationService.svc/Logoff"
headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
response = requests.request("POST",url, headers=headers, verify=False)
logoff_response=response.status_code

if logoff_response == 200:
	print("Logoff completed successfully with status_code: {}".format(logoff_response))
else:
	print("Logoff failed with status_code: {}".format(logoff_response))