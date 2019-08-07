from web3 import Web3, IPCProvider, HTTPProvider

from mycroft.util.log import LOG

user_accounts= {'<@ULE6JH5BN>' : '0x30e31d74f4f5f748680f740af0af73bd1a0ffa1c'}

def isImmune(immu):
	if immu:
		return "Immune"
	else :
		return "Not Immune"

def isVaccinate(vacc):
	if vacc:
		return "Yes"
	else:
		return "No"

def get_personal_information(id_user, text):
	password = id_user

	w3 = Web3(IPCProvider("../../All/mia/slackMia/Test/geth.ipc"))
	
	if(w3.isConnected()):
		LOG.info("It's connected")
	else:
		LOG.info("There is no connection")

	if(id_user in user_accounts):
		w3.personal.unlockAccount(user_accounts.get(id_user), password)
	else:
		account = w3.personal.newAccount(password)
		user_accounts[id_user] = account
		w3.personal.unlockAccount(account, password)
	
	abi = """ [{"constant":false,"inputs":[{"name":"eName","type":"string"},{"name":"ePhone","type":"string"},{"name":"eAddr","type":"string"}],"name":"setEmergencyCase","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"medicationName","type":"string"}],"name":"removeMedication","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getInsurance","outputs":[{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"medicationName","type":"string"},{"name":"dosage","type":"string"}],"name":"addMedication","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getPrimaryPersonalInfo","outputs":[{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"gchickenPox","type":"bool"},{"name":"gmeasles","type":"bool"},{"name":"ghepatitsb","type":"bool"},{"name":"gmedicalProblems","type":"string"},{"name":"gallergies","type":"string"}],"name":"setGeneralMedicalHistory","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getSecondaryPersonalInfo","outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"string"},{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"hevent","type":"string"}],"name":"addHistorical","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"pweight","type":"uint256"},{"name":"pheight","type":"uint256"},{"name":"pname","type":"string"},{"name":"psurname","type":"string"},{"name":"paddr","type":"string"},{"name":"pphone","type":"string"},{"name":"pgender","type":"string"},{"name":"pbirthday","type":"string"},{"name":"psmoker","type":"bool"},{"name":"pdrink","type":"string"},{"name":"pblood","type":"string"}],"name":"setAllPersonnalInfo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getEmergencyCase","outputs":[{"name":"","type":"string"},{"name":"","type":"string"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getGeneralMedicalHistory","outputs":[{"name":"","type":"bool"},{"name":"","type":"bool"},{"name":"","type":"bool"},{"name":"","type":"string"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"iName","type":"string"},{"name":"iNumber","type":"string"},{"name":"iAddress","type":"string"},{"name":"iExpiracy","type":"string"}],"name":"setInsurance","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}] """
	
	contract = w3.eth.contract(address = '0x14bbe469DEcFAeef110684811c7966df9DE74e05', abi = abi)
	return contract

def personal_information(id_user, text):

	contract = get_personal_information(id_user, text)
	
	if("personal" in text):
		LOG.info('~~~~~~~ Ok Bam bam bam ~~~~~~~~')
		name, suremane, gender, birthDate, blood = contract.functions.getPrimaryPersonalInfo().call()
		height, weight, address, smoker, drinker = contract.functions.getSecondaryPersonalInfo().call()
	
		if smoker:
			smokText = "Yes"
		else:
			smokText = "No"

		response = "Your personal informations are:\nName: " + name + "\nSurname: " + suremane + "\nBorn the: " + birthDate + "\nGender: " + gender + "\nHeight: " + str(height) + "cm.\nWeight: " + str(weight) + "kg\nBlood type: " + blood + "\nAddress: " + address + "\nHabits:\n - Smoker: " + smokText + "\n - Drink habits: " + drinker 

	elif("emergency" in text):
		name, phone, address = contract.functions.getEmergencyCase().call()
		response = "The information about your emergency contact are\nName: " + name + "\nPhone number: " + phone + "\nAddress: " + address

	elif("general" in text and ("medical" in text or "health" in text)):
		chickenPox, measles, hepatitisB, medicalProblems, allergies = contract.functions.getGeneralMedicalHistory().call()

		chickenPoxText = isImmune(chickenPox)
		measlesText = isImmune(measles)
		hepatitisBText = isVaccinate(hepatitisB)

		response = "Your personal general medical history is:\n Chicken Pox: " + chickenPoxText + "\nMeasles: " + measlesText + "\nHepatitis B vaccination: " + hepatitisBText + "\n Medical problems: " + medicalProblems + "\nAllergies: " + allergies

	elif("insurance" in text): 
		name, policy, address, expiracy = contract.functions.getInsurance().call()
		response = "Your insurance's information are:\n Name: " + name + "\n Policy number: " + policy + "\n Address: " + address + "\nExpiracy date: " + expiracy

	else:
		response = "I don't understand, can you say it another way?"


	return response