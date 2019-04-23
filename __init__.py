import base64
import subprocess
import re
import sys
import os
import time

from mycroft import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from adapt.intent import IntentBuilder
from os.path import join, exists
from termios import tcflush, TCIOFLUSH
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def generate_key(dir):
	pub_path = join(dir, 'publickey.txt')
	priv_path = join(dir, 'privatekey.txt')
	if os.path.exists(pub_path):
		pub_file = open(pub_path, 'r')
		pub_key = pub_file.read()
		pub_file.close()
		priv_file = open(priv_path, 'r')
		priv_key = priv_file.read()
		priv_file.close()
	else: 
		length = 1024
		priv_key = RSA.generate(length)
		pub_key = priv_key.publickey()
		pub_file = open(pub_path, 'w+')
		pub_file.write(pub_key)
		pub_file.close()
		priv_file = open(priv_path, 'w+')
		priv_key.write(priv_key)
		priv_file.close()
	return priv_key, pub_key

def encryption(message, pub_key):
	encryptor = PKCS1_OAEP.new(pub_key)
	cipher_message = encryptor.encrypt(message)
	encoded_message = base64.b64encode(cipher_message)
	return encoded_message

def decryption(encoded_message, priv_key):
	encryptor = PKCS1_OAEP.new(priv_key)
	cipher_message = base64.b64decode(encoded_message)
	message = encryptor.decrypt(cipher_message)
	return message

#command that activate the response to a speech.
def cmd(action, dir):
	test = TalkTest(action, dir)
	return test.talk_to_you()

#Class inheritant from MycroftSkill which allow the dialog.
class FirstTalk(MycroftSkill):

	#Initialization thanks to the super constructor.
	def __init__(self):
		super(FirstTalk, self).__init__(name="FirstTalk")
		self.talk = None
		self.conversation = False
		self.path = self._dir
	
	#Function calls whenever a line of InitialTalk is said
	#This function began the conversation between Mycroft and the user.
	@intent_handler(IntentBuilder("TalkFirstIntent").require("InitialTalk").build())
	def handle_talk_first__intent(self, message):
		if not self.talk:
			self.talk = True
			time.sleep(0.1)
		self.speak_dialog('talk.first')
		self.conversation = True

	#Function which is call when the user ask for help
	#TODO allow this function to be call in the conversation
	@intent_handler(IntentBuilder("TestMessageIntent").require("Help").build())
	def handle_test_message__intent(self, message):
		if self.talk:
			self.speak_dialog('talk.help')

	#Stop the conversation between Mycroft and the user
	def stop_conversation(self):
		self.conversation = False
		self.speak('Leave')

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
		
		

	#Test if what is said and what is waited match
	#Return the line of vocab that is a match
	def is_in(self, vocab, talk):
		voc_path = join('vocab/en-us/', vocab)
		path = join(self.dir, voc_path)
		file = open(path, 'r')
		lines = file.readlines()
		file.close()
		for line in lines:
			if talk.lower() in line.lower() or line.lower() in talk.lower():
				return line
		return None

	#Test the match of the vocab/what is said
	#Return the response associated.
	def response_talk(self, talk, vocab, response):
		if self.is_in(vocab, talk) is not None:
			resp_path = join('dialog/en-us/', response)
			path_dialog = join(self.dir, resp_path)
			file = open(path_dialog, 'r')
			content = file.read()
			file.close()
			return content 
		return None

	#Test if what is said match the vocab
	#If there is a match write the name on a file
	def save_name(self, talk, vocab):
		name_line = self.is_in(vocab, talk)
		if name_line is not None:
			result = re.split(name_line.lower(), talk.lower())
			name = re.split('\W+', result[1])
			file = open(self.data_path, 'w+')
			name_cap = name[1].capitalize()
			"""name_to_save = bytes(name_cap, 'utf8')
			encoded_name = encryption(name_to_save, self.pub_key)
			file.write(str(encoded_name))"""
			file.write(name_cap)
			file.close()

	#Return the name store in the file or None if it's empty.
	def get_name(self):
		if os.path.exists(self.data_path):
			file = open(self.data_path, 'r')
			name = file.read()
			file.close()
			return name
			"""return decryption(name[2:-1], self.priv_key).decode('utf8')"""
		return None


	#Return the given text by adding the name is one is found.
	#Return the help text if asked.
	def talk_to_you(self):
		talk = self.cmd
		talkative = self.response_talk(talk, 'Help.voc', 'Help.dialog')
		self.save_name(talk, 'Name.voc')
		if talkative is not None:
			return talkative
		if self.get_name() is not None:
			talk += ", " + self.get_name()
		return talk


#create the skill and load it in mycroft when it is launch. 
def create_skill():
	return FirstTalk()

