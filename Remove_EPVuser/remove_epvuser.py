###
# Replace PVWA_LB_HERE with your CyberArk PVWA Load Balancer Name
# Add your CyberArk system Accounts exceptions list. Running this script first without uncommenting the lines will give you an idea about accounts which are going to be removed
###

import requests
import time
import getpass
import base64
import urllib3
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
	username = input("Enter your Vault username:")
	password = getpass.getpass("Enter Vault password:")
except:
	print('ERROR', err)
	
epv_user = []
f_epvusr = open("epv_user_details.txt","a+",encoding="utf-8")
f = open("removed_user_with_group.csv","w")

## Replace below exception users and Add your CyberArk system accounts below so that script will not remove those accounts.
exception = ['PSMAPP1', 'PSMAPP2', 'PSMGW1', 'PSMGW2', 'PVWAAPP1', 'PVWAAPP2', 'PVWAGW1', 'PVWAGW2', 'PASSWORDMANAGER', 'PSMPAPP', 'PSMPGW', 'DR', 'Backup', 'Operator', 'Administrator', 'Master']

url = "https://PVWA_LB_HERE/PasswordVault/WebServices/auth/CyberArk/CyberArkAuthenticationService.svc/Logon"
headers = { 'Content-Type': 'application/json', 'Cache-Control':'max-age=300'}
data = '{ "username":"'+username+'", "password":"'+password+'", useRadiusAuthentication":"false", "connectionNumber":"1"}'
response = requests.request("POST", url, headers=headers, data=data, verify=False)
login_response = response.status_code
output_response = response.json()
auth_token = output_response['CyberArkLogonResult']
time.sleep(1)

if login_response == 200:
	print("Logon completed successfully with status_code: {}".format(login_response))
else:
	print("Logon failed with status_code: {}".format(login_response))

URL_get_epvusers = "https://PVWA_LB_HERE/PasswordVault/API/Users/"
headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
response = requests.request("GET", URL_get_epvusers, headers=headers, verify=False)
time.sleep(1)
statusCode = response.status_code
output_response = response.json()

if statusCode == 200:
	print("Pulled epv user details successfully with status_code: {}".format(statusCode))
	for j in output_response["Users"]:
		epv_usr = j['username'] + ': ' + str(j['id'])
		epv_user.append(epv_usr)
	for u in epv_user:
		usr, id = u.split(': ')
		URL_epvuser_details = "https://PVWA_LB_HERE/PasswordVault/API/Users/%s/" %id
		headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
		response = requests.request("GET", URL_epvuser_details, headers=headers, verify=False)
		time.sleep(1)
		statusCode = response.status_code
		output_response = response.json()
		epoch_time = output_response["lastSuccessfulLoginDate"]
		date_time = datetime.fromtimestamp(epoch_time)
		month_old = datetime.now() - timedelta(days=30)
		if output_response["userType"] == "EPVUser" and month_old > date_time and usr not in exception:
			print("%s, UserType= %s, enableUser= %s, suspended= %s, LastLogin= %s" %(usr,output_response["userType"],output_response["enableUser"],output_response["suspended"],date_time))
			f_epvusr.write("%s, UserType= %s, enableUser= %s, suspended= %s, LastLogin= %s\n" %(usr,output_response["userType"],output_response["enableUser"],output_response["suspended"],date_time))
			f_epvusr.write("%s\n" %str(response.text))
			if "'groupsMembership': []," not in output_response:
				for g in output_response["groupsMembership"]:
					f.write("%s, userType= %s, enableUser= %s, suspended= %s, authenticationMethod= %s, groupName= %s, groupType= %s\n" %(usr,output_response['userType'],output_response["enableUser"],output_response["suspended"],output_response["authenticationMethod"],g["groupName"],g["groupType"]))
					if "'groupMembership': [], 'id':" in str(output_response):
						f.write("%s, userType= %s, enableUser= %s, suspended= %s, authenticationMethod= %s, No Group\n" %(usr,output_response['userType'],output_response["enableUser"],output_response["suspended"],output_response["authenticationMethod"]))
						
					### Uncomment Below Lines ONLY AFTER adding the correct accounts names in exception ###
					#
					#URL_epvuser_delete = "https"//PVWA_LB_HERE/PasswordVault/api/Users/%s/" %id
					#headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
					#respnse = requests.request("DELETE", URL_epvuser_delete, headers=headers, verify=False)
					#time.sleep(1)
					#statusCode=respnse.status_code
					#print(respnse)
					#if "204" in str(statusCode):
					#	print("Successfully removed")
					#	f_epvusr.write("Successfully removed\n")
					#
					f_epvusr.write("==========================================================================================================================================\n\n")
else:
	print("Failed to pull epv user details with status_code: {}".format(statusCode))
	
f_epvusr.close()
f.close()
	
url = "https://PVWA_LB_HERE/PasswordVault/WebServices/auth/Shared/RestfulAuthenticationService.svc/Logoff"
headers = { 'Content-Type': 'application/json', 'Authorization':auth_token}
response = requests.request("POST",url, headers=headers, verify=False)
logoff_response=response.status_code

if logoff_response == 200:
	print("Logoff completed successfully with status_code: {}".format(logoff_response))
else:
	print("Logoff failed with status_code: {}".format(logoff_response))
					