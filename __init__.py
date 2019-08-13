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

user_accounts= {'<@ULE6JH5BN>' : '0xF95c934512C8b46b0DDe21Cc6B059dd60d374AB7'}
w3 = Web3(Web3.IPCProvider("../../All/mia/slackMia/Test/geth.ipc"))
LOG.info(os.getcwd())	

#command that activate the response to a speech.
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

		
	#Function calls whenever a line of InitialTalk is said
	#This function began the conversation between Mycroft and the user.
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
		self.speak('Bye bye')

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

	#test if the utterance match with one of the sentence in the voc file
	#if there is a match, return the name of the file and the line 
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


	#If there is a symbol in the dialog file, Microft change it to the appropriate personal data 
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

	def isImmune(self, immu):
		if immu:
			return "Immune"
		else: 
			return "Not Immune"

	def isVaccinate(self, vacc):
		if vacc:
			return "Yes"
		else:
			return "No"

	def is_personal_info(self, talk):
		password = "marion"


		if(w3.isConnected()):
			LOG.info("Connection successed")
		else:
			LOG.info("Connection failed")

		id_user = "patient1"		
		
		account = w3.personal.newAccount(password)
		user_accounts[id_user] = account
		w3.personal.unlockAccount(account, password)

		LOG.info("Account created")

		
		with open ("../../All/mia/slackMia/api.json") as f:
			info_json = json.load(f)

		abi = info_json

		contract = w3.eth.contract(address = '0xa495BD57133d4d4adC2D4C665A0bF7cdfADeaD1d', abi = abi)

		LOG.info("Contract check")
		name, surname, gender, date, blood = contract.call().getPrimaryPersonalInfo()

		response = name + " " + surname + " you are a " + gender + " your are born the " + date + " and your blood type is " + blood

		return response

	#Test the match of the vocab/what is said
	#Return the response associated.
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

	#Return the the predefinite text if that match a voc file
	#Return the deep response if none text is found.
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

