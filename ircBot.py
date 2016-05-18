from random import randint
import socket, string
import os.path

## Issue where sending ":" as the first character in chat crashes the bot.
## www.instructables.com/id/Twitchtv-Moderator-Bot/?ALLSTEPS
## COMMANDS
##
## !addcom  - adds a command to command list 	"!addcom <commandName> <command>"
## !adduser - adds a user to the admins list	"!adduser <userName>"
## !delcom  - deletes a command 		"!delcom <commandName>"
## !deluser - deletes a user			"!deluser <userName>"

rootAdmins = ["valkrinbot", "tylairlol", "anderak"]
admins = []
rootCommands = ["!addcom", "!addadmin", "!delcom", "!deladmin"]
globalCommands = ["!admins", "!commands", "!help", "!roll"]
customCommands = {"!test": "Data for test command!"}

jsonFileName = "config.json"
readbuffer = ""

if os.path.isfile(jsonFileName):
    print "The config file exists. Getting content..."
    config = json.load(open(jsonFileName, 'r'))
    HOST = config["HOST"]
    PORT = config["PORT"]
    CHAN = config["CHAN"]
    NICK = config["NICK"]
    PASS = config["PASS"]
else:
    print "The config does not exist. Exiting."
    return

s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS " + PASS + "\r\n")
s.send("NICK " + NICK + "\r\n")
s.send("JOIN " + CHAN + "\r\n")
MODT = False


def sendMessage(message):
	s.send("PRIVMSG #valkrinbot :" + message + "\r\n")

def consumeCommand(username, command):
	if command[0] == "!roll":
		if int(command[1]) <= 100 and int(command[1]) > 0:
			temp = ""
			temp += username + " rolls "
			temp += str(randint(0, int(command[1]))) + " out of " + command[1] + "."
			sendMessage(temp)
		else:
			print "FAILED: command " + command[1] + "."
		return
	if command[0] == "!addcom":
		if command[1] not in rootCommands and command[1] not in globalCommands and command[1] not in customCommands:
			temp = ""
			for item in command[2:]:
				temp += item + " "
			customCommands[command[1]] = temp
			print "SUCCESS: " + command[1] + " is now a command."
		else:
			print "FAILED: command " + command[1] + " already exists."
		return
	elif command[0] == "!addadmin":
		if command[1] not in rootAdmins and command[1] not in admins:
			admins.append(command[1])
			print "SUCCESS: " + command[1] + " is now an admin."
		else:
			print "FAILED: " + command[1] + " is already an admin."
		return
	elif command[0] == "!delcom":
		if command[1] in customCommands:
			customCommands.pop(command[1])
			print "SUCCESS: command " + command[1] + " deleted."
		else:
			print "FAILED: command " + command[1] + " cannot be deleted or doesn't exist."
		return
	elif command[0] == "!deladmin":
		if command[1] in admins:
			admins.pop(command[1])
			print "SUCCESS: admin " + command[1] + " deleted."
		else:
			print "FAILED: admin " + command[1] + " cannot be deleted or doesn't exist."
		return
	elif command[0] == "!admins":
		temp = ""
		for item in rootAdmins:
			temp += item + " "
		for item in admins:
			temp += item + " "
		print "Admins: " + temp
		sendMessage("Admins: " + temp)
		return
	elif command[0] == "!commands":
		temp = ""
		for item in rootCommands:
			temp += item + " "
		for item in globalCommands:
			temp += item + " "
		for item in customCommands:
			temp += item
		print "Commands: " + temp
		sendMessage("Commands: " + temp)
		return
	elif command[0] == "!help":
		print "Help message."
		sendMessage("Hi! My name is Valkrinbot, I'm here to help Valkrin by answering common questions and giving general help. I accept commands in the format \"!commandname\", type \"!commands\" to see a list of current commands.")
		return
	else:
		print command[0] + " " + customCommands[command[0]]
		sendMessage(command[0] + " " + customCommands[command[0]])
		return


while True:
	readbuffer = readbuffer + s.recv(1024)
	temp = string.split(readbuffer, "\n")
	readbuffer = temp.pop()

	for line in temp:
		if(line[0] == "PING"):
			s.send("PONG %s\r\n" %line[1])
		else:
			print line
			parts = string.split(line, ":")
			if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
				try:
					message = parts[2][:len(parts[2]) - 1]
				except:
					message = ""
				usernamesplit = string.split(parts[1], "!")
				username = usernamesplit[0]

				if MODT:
					print username + ": " + message

					if message[0] == "!":
						messagesplit = string.split(message, " ")
						print messagesplit
						if messagesplit[0] in globalCommands or messagesplit[0] in customCommands:
							consumeCommand(username, messagesplit)
						elif (messagesplit[0] in rootCommands and (username in admins or username in rootAdmins)):
							consumeCommand(username, messagesplit)
						else:
							print username + " does not have permission to use command " + messagesplit[0] + ", or command does not exist."

				print parts
				for l in parts:
					if "End of /NAMES list" in l:
						MODT = True
						sendMessage("Hello! ValkrinBot is online!")
