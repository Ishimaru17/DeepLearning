from web3 import Web3, IPCProvider, HTTPProvider
import json
import time



#w3 = Web3(IPCProvider("../../../../home/ishimaru/Documents/WIT/All/mia/slackMia/Test/geth.ipc"))

w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/94df8f865dae4697a14fb488c0f558aa'))

if (w3.isConnected()):
	print("it's connected")
else:
	print("not connected")


account = w3.personal.newAccount('marion')
w3.eth.defaultAccount = w3.eth.accounts[0]
w3.personal.unlockAccount(w3.eth.accounts[0], 'marion')

w3.miner.start(2)
while(w3.eth.getBalance(w3.eth.accounts[0])<=10000000):
	time.sleep(3)
w3.miner.stop()

with open ("./api.json") as f:
	info_json = json.load(f)

with open ("./bytecode.json") as f:
	bytecode_info = json.load(f)

abi = info_json
bytecode = bytecode_info['object']

contract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = contract.constructor().transact()

tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

print(tx_receipt.contractAddress)

first_contract = w3.eth.contract(address = tx_receipt.contractAddress, abi= abi,)

with open("./health_record_template.json") as f:
	record = json.load(f)

print('Setting personal information')
personal = "Personal information"
smoker = False
if record[personal]["Habits"]["Smoker"] == "Yes":
	smoker = True

tx_hash = first_contract.functions.setAllPersonnalInfo(
	record[personal]["Weight"],
	record[personal]["Height"],
	record[personal]["Name"],
	record[personal]["Surname"],
	record[personal]["Address"],
	record[personal]["Phone number"],
	record[personal]["Gender"],
	record[personal]["Birth date"],
	smoker,
	record[personal]["Habits"]["Drinker"],
	record[personal]["Blood type"]
	).transact()

w3.eth.waitForTransactionReceipt(tx_hash)

print('Setting Emergency information')
emergency = "In case of Emergency"

tx_hash = first_contract.functions.setEmergencyCase(
	record[emergency]["Name"],
	record[emergency]["Phone number"],
	record[emergency]["Address"]
	).transact()

w3.eth.waitForTransactionReceipt(tx_hash)

print('Setting General Medical History')
general = "General Medical History"

chickenPox = False
measles = False
hepatitisB = False

if record[general]["Chicken pox"] == "Immune":
	chickenPox = True

if record[general]["Measles"] == "Immune":
	measles = True

if record[general]["Hepatitis B vaccination"] == "Yes":
	hepatitisB = True

tx_hash = first_contract.functions.setGeneralMedicalHistory(
	chickenPox,
	measles,
	hepatitisB,
	record[general]["List of any medical problems"],
	record[general]["List of allergies"]
	).transact()

w3.eth.waitForTransactionReceipt(tx_hash)

print("Setting medical insurance")
insurance = "Medical insurance"

tx_hash = first_contract.functions.setInsurance(
	record[insurance]["Name"],
	record[insurance]["Policy Number"],
	record[insurance]["Address"],
	record[insurance]["Expiracy date"]
	).transact()

w3.eth.waitForTransactionReceipt(tx_hash)

print("All the setting are ok!")





#Account "0x30e31d74f4f5f748680f740af0af73bd1a0ffa1c"