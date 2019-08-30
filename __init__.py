import base64
import subprocess
import re
import sys
import os
import json
import time

from mycroft import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from adapt.intent import IntentBuilder
from os.path import join, exists
from importlib import reload
from web3 import Web3

HOME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HOME_DIR)
import mia_deep
import blockchain

#Connection to the locale blockchain (path to change or convert to an HTTPProvider for an online blockchain)
w3 = Web3(Web3.IPCProvider("../../All/mia/slackMia/Test/geth.ipc"))

#Command that activate the response to a speech.
def cmd(talk, dir):
	speech = TalkTest(talk, dir)
	return speech.talk_to_you()

#Class inheritant from MycroftSkill which allow the dialog.
class DeepLearning(MycroftSkill):

	#Initialization thanks to the super constructor.
	def __init__(self):
		super(DeepLearning, self).__init__(name="DeepLearning")
		self.talk = None
		self.conversation = False
		self.path = self._dir

		
	"""If a sentence of TalkFirstIntent is said, this function is triggered. 
	This is the function that starts the MIA Skill."""
	@intent_handler(IntentBuilder("TalkFirstIntent").require("InitialTalk").build())
	def handle_talk_first__intent(self, message):
		if not self.talk:
			self.talk = True
			time.sleep(0.3)
		self.speak_dialog('InitialTalk.voc')
		self.conversation = True

	#Stop the conversation between Mycroft and the user
	def stop_conversation(self):
		self.conversation = False
		self.speak('See you soon.')

	#If there is a talk, stop it by calling the corresponding function
	def stop(self, message = None):
		if self.talk:
			self.stop_conversation()

	#As long as this function return true, the conversation is still on
	def converse(self, utterance, lang):
		if utterance:
			utterance = utterance[0]
			if self.conversation:
				if "quit" in utterance or "exit" in utterance:
					self.stop_conversation()
					return True
				else: 
					the_talk = cmd(utterance, self.path)
					self.speak(the_talk)
					return True
				return True
		return False


#Class of the different talking.
class TalkTest:
	def __init__(self, cmd, dir):
		self.cmd = cmd
		self.dir = dir
		self.data_path = join(self.dir, 'name.txt')

	"""Test if the utterance match with one of the sentence in the voc file
	if there is a match, return the name of the file and the line """
	def is_in_voc(self, talk):
		path = join(self.dir, 'vocab/en-us/')
		for name in os.listdir(path):
			f = open (path+name, 'r')
			lines = f.readlines()
			f.close()
			for line in lines:
				if len(talk) >= 5 and talk.lower() in line.lower() or line.lower() in talk.lower():
					return (line, name)
		return None


	#If there is the symbol {n} in the dialog file, Microft change it with the name of the user if it's saved
	def personalise_response(self, resp):
		if resp.find("{n}") >= 0:
			if os.path.exists(self.data_path):
				file = open(self.data_path, 'r')
				name = file.read()
				file.close()
				resp_tab = re.split("{n}", resp)
				response = resp_tab[0] + name + resp_tab[1]
				return response
			else:		
				resp_tab = re.split("{n}", resp)
				response = resp_tab[0] + resp_tab[1]
				return response
		return resp

	#Returns a sentence according to the status of the boolean immune
	def isImmune(self, immu):
		if immu:
			return "you are immune to "
		else: 
			return "you are not immune to"

	#Returns a sentence according to the status of the booolean vaccine
	def isVaccinate(self, vacc):
		if vacc:
			return "you are vaccinate for "
		else:
			return "you are not vaccinate for "

	#Get personal information from the blockchain. (This function can't be split in multiple ones)
	def is_personal_info(self, talk):
		#TODO: Get the password from the current user
		password = "marion"

		text = talk.lower()

		if(w3.isConnected()):
			LOG.info("Connection successed")
		else:
			LOG.info("Connection failed")

		#TODO: Get the user identifier for the current user
		id_user = "patient1"		
		
		#TODO: Stop creating an account for each transaction and connect with the account of the user
		#Creation of a new account to access the blockchain
		account = w3.personal.newAccount(password)

		#Unlock of the account to allow transaction (that must be done here, even if the account is create earlier in the code)
		w3.personal.unlockAccount(account, password)

		#Get the ABI of the smart contract 
		with open ("../../All/mia/slackMia/api.json") as f:
			info_json = json.load(f)

		abi = info_json

		#TODO: Get the address dynamically
		#Get the address where the contract has been set.
		contract = w3.eth.contract(address = '0x622556A0A2987EFD8D857B8249d62c18a7f2255f', abi = abi)

		#Get the personal information from the patient which is link to the contract
		if("personal" in text):
			name, surname, gender, date, blood = contract.call().getPrimaryPersonalInfo()
			height, weight, address, smoker, drinker = contract.call().getSecondaryPersonalInfo()
			if smoker:
				smokeText = "you are a smoker"
			else:
				smokeText = "you are not a smoker"

			response = name + " " + surname + " you are a " + gender + " your are born the " + date + " and your blood type is " + blood + " you measure " + str(height) + " cm and you weigh " + str(weight) + "kg you live at " + address + " " + smokeText + " and you drink " + drinker
		
		#Get the emergency information from the patient which is link to the contract
		elif("emergency" in text):
			name, phone, address = contract.call().getEmergencyCase()
			response = "The name of your emergency contact is " + name + " his her phone number is " + phone + " and his her address is " + address
		
		#Get the general medical information from the patient which is link to the contract
		elif("general" in text and ("medical" in text or "health" in text)):
			chickenPox, measles, hepatitisB, medicalProblems, allergies = contract.call().getGeneralMedicalHistory()

			chickenPoxText = self.isImmune(chickenPox)
			measlesText = self.isImmune(measles)
			hepatitisBText = self.isVaccinate(hepatitisB)

			response = chickenPoxText + " chicken pox " + measlesText + " measles " + hepatitisBText + " hepatitis B your medical problems are " + medicalProblems + " and you are allergic to " + allergies

		#Get the insurance information from the patient which is link to the contract
		elif("insurance" in text):
			name, policy, address, expiracy = contract.call().getInsurance()
			response = "Your insurance name is " + name + " which is locate in " +  address + " your policy number is " + policy + " its expire the " + expiracy

		#Get the answer from the deeplearning
		else:
			response = mia_deep.input(text)

		return response

	""" Test if the user input correspond to one of the sentence in the voc files, or if the user ask for information that are in the blockchain.
	Returns the appropriate answer.
	"""
	def response_talk(self, talk):
		voc = self.is_in_voc(talk)
		if voc is not None:
			voc_path = voc[1] + '.dialog'
			if voc[1] == "Name.voc":
				self.save_name(talk, voc[0])
			resp_path = join('dialog/en-us/', voc_path)
			path_dialog = join(self.dir, resp_path)
			if os.path.exists(path_dialog):
				file = open(path_dialog, 'r')
				content = file.read()
				file.close()
				content_pers = self.personalise_response(content)
				return content_pers

		if "information" in talk.lower():
			return self.is_personal_info(talk)

		return None
  
	#Save name in a file
	def save_name(self, talk, vocab):
		if talk is not None:
			result = re.split(vocab.lower(), talk.lower())
			name = re.split('\W+', result[1])
			name_cap = name[1].capitalize()
			file = open(self.data_path, 'w+')
			file.write(name_cap)
			file.close()

	#Returns the the predefinite text if that match a voc file
	#Returns the information from the blockchain if asked
	#Returns the deep response if none text is found.
	def talk_to_you(self):
		talk = self.cmd
		talkative = self.response_talk(talk)
		if talkative is not None:
			return talkative
		else: 
			return mia_deep.input(talk)


#create the skill and load it in mycroft when it is launch. 
def create_skill():
	return DeepLearning()

