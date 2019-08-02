from web3 import Web3, IPCProvider, HTTPProvider

from mycroft.util.log import LOG


w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/94df8f865dae4697a14fb488c0f558aa'))
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
	'''
	geth_path = "../../../blockchain/Test/geth.ipc"
	w3 = Web3(IPCProvider(geth_path))
	'''
	if(w3.isConnected()):
		LOG.info("It's connected")
	else:
		LOG.info("There is no connection")

	if(id_user in user_accounts):
		w3.personal.unlockAccount(user_accounts.get(id_user), password)
	else:
		account = w3.personal.newAccount(password)
		user_accounts[is_user] = account
		w3.personal.unlockAccount(account, password)


	abi_path =  "./api.json"
	with open(abi_path) as f:
		abi = json.load(f)
	contract = w3.eth.contract(address = '0xd2C3A976FC87D1aD95CD3a6F8ab4955b6017e943', abi = abi)

def personal_information(id_user, text):

	get_personal_information(id_user, text)
	
	if("personal" in text):
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