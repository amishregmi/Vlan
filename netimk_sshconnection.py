import paramiko
import re 
import netmiko
from netmiko import ConnectHandler
import send_email

#from netmiko import *

host = "###"
user = "####"
pw = "####"
platform = "#######"

#Commands
CMD_CONFIG_PAGING_DISABLED = "config paging disable"
CMD_SHOW_AP_SUMMARY = "show ap summary"
CMD_SHOW_AP_CONFIG_GENERAL = "show ap config general "

problem_vlans = [540]

debug = False;


def main():
	device = ConnectHandler(device_type=platform, ip=host, username=user, password=pw)

	device.send_command(CMD_CONFIG_PAGING_DISABLED)
	output = device.send_command(CMD_SHOW_AP_SUMMARY)[7:]
	#print(type(output)) #<class 'str'>

	#output is a blob of string returned by the command above. Break the blob
	#into multiple lines of string and store them into the list
	#the first 7 elements of the list can be ignored
	output = output.split('\n')[7:]

	#this list will contain the names of all the aps queries above
	ap_list = []

	#parse the string and store only the ap names in ap_list
	for line in output:
		line = line.split(' ')[0]
		if 'ap_' in line:
			ap_list.append(line.strip())


	apInfo = {}
	for ap in ap_list:
		try:
			result = device.send_command(CMD_SHOW_AP_CONFIG_GENERAL + ap).split('\n')

			#run through the result 
			for line in result:
				
				# if the first few strings in the line matches
				# "AP Mode .." and the last few line matches "FlexConnect"
				#store that ap in the flexconnect_aplist list
				if line[0:len("AP Mode ..")] == "AP Mode ..":
					beginQueryIndex = len(line) - len("FlexConnect");
					
					if line[beginQueryIndex: len(line)] == "FlexConnect":
						apInfo[ap] = result;
		except OSError as e:
			print("Error Occured for ap ", ap)
			print(e)



	parsedData = parseAPData(apInfo)

	if(debug == True):
		debugOutput(parsedData)
	else:
		productionOutput(parsedData)

	device.disconnect()


def parseAPData(apDict):
	'''
	The dictionary in the parameter contains an ap as a key and a list of 
	strings retrieved from the query 'show ap config general ap_name' as value.
	The blob has to be parsed to extract:
	1. Ap Name
	2. Country
	3. Group VLAN ACL
	4. Cisco AP Group Name
	5. Native Id
	'''
	parsedData = {}
	for key, val in apDict.items():
		attrib = {}
		problemVlansFound = False
		for i in range(0, len(val)):
			line = val[i]

			if('Country code' in line):
				attrib['Country Code'] = line;

			if('Cisco AP Group Name' in line):
				attrib['Cisco Ap Group Name'] = line

			if('FlexConnect Vlan mode :' in line):
				attrib['Vlan'] = val[i: i+5]
				vlanList = getVlans(val[i: i+5]);

				if(list(set(problem_vlans) & set(vlanList)) != []):
					problemVlansFound = True
				else:
					break;

			if 'Native ID :' in line:
				attrib['Native ID'] = line

		if problemVlansFound:
			parsedData[key] = attrib

	return parsedData


def getVlans(blobList):
	'''This function takes a list of
		strings and returns a list
		of vlans mentioned on those
		lines
	'''
	WlanList = []
	# print(blobList);
	for line in blobList:
		try:
			WlanList.append(int(re.search(r"[0-9]{3,4}", line).group()))
		except AttributeError as e:
			pass;


	return WlanList


def debugOutput(parsedData):
	'''For Debugging Purpuse only'''
	for key, val in parsedData.items():
		print(key)
		for k, v in val.items():
			if type(v) == type('a'):
				print(v.replace('.',''))
			elif type(v) == type([]):
				for item in v:
					print(item.replace('.', ''))

		print("\n\n")



def productionOutput(parsedData):
	print("Problem vlan found in the following: ")

	#this list stores NativeId in the 0th index and
	#vlan in the rest of the indexes
	output = "";
	for key, val in parsedData.items():
		output +=key + ": ";
		vlans = []
		for k, v in val.items():
			if type(v) == type([]): #if the next item is a list, only print the WLANS
				for i in range(len(v)):
					vlan = re.search(r"[0-9]{3,4}", v[i])
					if vlan!= None:
						vlans.append(vlan.group() + " ");
		output += ''.join(vlans)
		output += '\n'

	print(output);
	send_email.email(output)


if __name__ == '__main__':
	main()