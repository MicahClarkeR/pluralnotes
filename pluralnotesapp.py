#!/usr/bin/env python3
import os
import sys
import colorama
import shutil
import re
from datetime import date
from time import sleep

colorama.init()

# TODO: Test on Windows
# TODO: Check on this: "On some platforms, including FreeBSD and Mac OS X, setting environ may cause memory leaks. Refer to the system documentation for putenv()." See line 12 for why
# os.remove can remove files. Specify path.

notesDir = os.environ['HOME'] + '/.pluralnotes' # Used to define the main notes directory and/or work with it.
sharedDir = notesDir + '/sharednotes' # Location of shared directory
archiveDir = notesDir + '/archivednotes' # Location of archive directory (deleted users' notes)
sharedSelection = "0" # Must be 0, else you may accidentally call an if statement. Used in a while loop to determine user actions and sometimes as an exit condition. There's probably a way to define this later and save a few lines, but make that a TODO since basic functionality comes first.
todayDate = str(date.today()) # Used to append the date onto the end of files, and hide the date when casually viewing them.

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def dirChanger(dirName):
	if os.path.isdir(dirName) == False: os.mkdir(dirName)
	os.chdir(dirName)
	workingDir = os.path.dirname

# Login sequence; tries to account for upper/lowercase and exits if the user requests it, else loops prompt until a valid login is entered. Allows users to create nonexistent username directories as long as they don't violate these restrictions, or log into an existing one.
# TODO: Check if a username including a backslash is a problem at all.
# TODO: Figure out password authentication and directory encryption so inter-username privacy is possible. This is meant to be a multiuser notekeeping utility on one shared computer account, so passwords are kind of important for that. Also MAKE SURE that the passwords are stored encrypted, and encrypt the entered password with the same hash to compare. People reuse passwords a lot and it's a security hazard to store them in plaintext. Make sure the password is not displayed as it's typed, too.
def login():
	global username
	while 1:
		username = input(" Enter your name (case-sensitive), or q to exit: ")
		# If user does not yet exist:
		# Deal with whitespaces and empty strings
		if os.path.isdir(notesDir + "/" + username) == False:
			if username.isspace() == True or " " in username or "\n" in username or "\t" in username:
				clear()
				print(" Usernames cannot contain spaces, tabs, or new lines. Please enter a valid username.")
			elif username == False or username == "":
				clear()
				print(" Please enter a valid username.")

			# Disallow reserved shared directory name to avoid naming conflict
			elif username == "sharednotes" or username == "archives":
				clear()
				print(" Name reserved for shared notes or archives. Please enter a valid username.")

			# Give the user a way to exit the program from this prompt so they're not stuck looping endlessly until they make a user
			elif username.lower() == "q":
				clear()
				print("See you next time!")
				sys.exit(0)

			# Ask if the person wants to create user if it doesn't already exist, and create them if yes
			else:
				print(" This user does not exist. Would you like to create a user called " + username + "?")
				userCheck = input(" Input <y/n>: ").lower()
				if userCheck == "y" or userCheck == "yes":
					# os.mkdir(username)
					dirChanger(username)
					if os.path.isdir("data") == False: os.mkdir("data")
					os.chdir(notesDir)
					print (" " + username + " created. You may now log in!")

		# Log in valid existing users and proceed to the actual program
		# TODO: Add password authentication and decryption of logged-in user.
		elif os.path.isdir(notesDir + "/" + username) == True:
			userDir = notesDir + "/" + username
			if os.path.isfile(userDir + "/data/settings.txt") == False:
				if os.name == "nt":
					defaultEditor = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'notepad'
				else:
					defaultEditor = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'nano'
				f = open(notesDir + "/" + username + "/data/settings.txt", "a")
				f.write(defaultEditor + "\n")
				f.write("10" + "\n")
				f.write("True" + "\n")
				f.write("False" + "\n")
				f.write("-" + "\n")
				f.write("Warning: Do not edit spacing!" + "\n")
				f.write("If manually editing settings, True/False must be capitalized. If you mess it up, don't worry- you can either delete this file (the program will remake it) or reset to the default in settings.")
				f.write("""Settings in order:
				Editor
				Page size
				Include date in new note names
				Include username in new note names""")
			break

		# Deal with edge cases and weird inputs, because you just know that someone is going to break this in an unexpected way.
		else: print(" Please enter a valid username.")


def paginateDir(dirName):
	feedback = ""
	settingsFile = os.environ['HOME'] + '/.pluralnotes' + "/" + username + "/data/settings.txt"
	settings = open(settingsFile, 'r').readlines()
	editor = str(settings[0]).strip()
	fileCount = int(str(settings[1]).strip())
	navigator = 0
	# Create a list of working directory contents. Sort the list alphabetically.
	dirContents = os.listdir()
	dirContents = sorted(dirContents, key=str.lower)
	dirContentsLength = len(dirContents)
	selection = 0 # Used by user for input, and to break loop on request
	bottomPageNumber = 0 # Lower limit of a page
	pageCount = 1 # Which page we're on. Needs to be separate from bottomPageNumber because that variable increments by the number in fileCount, and page number increments by one.
	topPageNumber = bottomPageNumber + fileCount # Upper limit of a page.
	if len(dirContents) == 0:
		while navigator != "q":
			print()
			print(" No notes here!")
			print()
			print("\x1b[31m" + " q: quit" + "\x1b[0m")
			if feedback != "":
				print()
			print("\x1b[33m" + " " + feedback + "\x1b[0m")
			navigator = input(" Enter selection: ").lower()
			if navigator == "q":
				clear()
				break
			else:
				clear()
				feedback = "Invalid input."
	else:
		holderList = []
		# Remove folders from directory list- there's bound to be a better way to do it but this works for now.
		for elem in dirContents:
			isFile = os.path.isfile(elem)
			if isFile == True:
				holderList.append(str(elem))
		dirContents = holderList
		dirContents = sorted(dirContents, key=str.lower)
		search = False
		outOfNotes = False
		while selection != "q":
			print()
			print(" Page " + str(pageCount))
			print()
			# Paginate directory. Sort of an odd way to do it, but it works and I couldn't get another method working. Still learning Python! Definitely an area to refactor later.
			for elem in dirContents[bottomPageNumber:topPageNumber]:
				print(str(" " + str(dirContents.index(elem))) + ". " + str(elem)) # Yes, the outermost string is needed. It throws a type error otherwise.
			print()
			print("\x1b[31m" + " n: next page" + "\x1b[0m")
			print("\x1b[33m" + " b: previous page" + "\x1b[0m")
			print("\x1b[32m" + " s: search for notes" + "\x1b[0m")
			if search == True:
				print("\x1b[36m" + " c: clear search" + "\x1b[0m")
			print("\x1b[34m" + " e: read/edit note" + "\x1b[0m")
			print("\x1b[35m" + " d: delete note" + "\x1b[0m")
			print("\x1b[31m" + " q: quit" + "\x1b[0m")
			if feedback != "":
				print()
			print("\x1b[33m" + " " + feedback + "\x1b[0m")
			# User input time!
			navigator = input(" Enter selection: ").lower()
			# Address running out of notes so the user can't iterate through empty pages
			if navigator == "n" and dirContentsLength < topPageNumber + pageCount:
				clear()
				feedback = "No more notes."
			elif navigator == "b" and pageCount == 1:
				clear()
				# Fixes weird change in size of list that happens otherwise by resetting to page "one" (0)
				bottomPageNumber = 0
				topPageNumber = bottomPageNumber + fileCount
				pageCount = 1
				feedback = "You're already on the first page!"
			# Regular navigation
			elif navigator == "n":
				clear()
				# Iterate to next page.
				bottomPageNumber = bottomPageNumber + fileCount
				topPageNumber = bottomPageNumber + fileCount
				pageCount = pageCount + 1
				feedback = ""
			elif navigator == "b" and pageCount != 1:
				clear()
				# Iterate to previous page.
				bottomPageNumber = bottomPageNumber - fileCount
				topPageNumber = bottomPageNumber + fileCount
				pageCount = pageCount - 1
				feedback = ""
			# Address trying to change pages when there are no notes
			elif navigator == "n" and len(dirContents[bottomPageNumber:topPageNumber]) == 0:
				clear()
				feedback = ""
			elif navigator == "b" and len(dirContents[bottomPageNumber:topPageNumber]) == 0:
				clear()
				feedback = ""
			# Search function
			elif navigator == "s":
				# Ask for regex pattern, compile it, then iterate through the directory checking to see if notes match. If the notes do match, they're added to a list. At the end of the iterations, set dirContents (the variable used to print contents) equal to the results stored in this list and sort as usual. If there are no matches, re-sort the directory to show all notes again and notify the user. Also set search = True to show the "clear search" option.
				search = True
				regMatchList = []
				searchTerm = str(input(" Enter search term (regex): "))
				clear()
				pattern = re.compile(searchTerm)
				for elem in dirContents:
					match = re.search(pattern, elem)
					if match:
						regMatchList.append(elem)
				dirContents = sorted(regMatchList, key=str.lower)
				if dirContents == []:
					clear()
					feedback = "No notes matching term found."
					search = False
					dirContents = os.listdir()
					holderList = []
					for elem in dirContents:
						isFile = os.path.isfile(elem)
						if isFile == True:
							holderList.append(str(elem))
					dirContents = holderList
					dirContents = sorted(dirContents, key=str.lower)
			# Clear search, redo list
			elif navigator == "c":
				clear()
				feedback = "Search cleared."
				search = False
				dirContents = os.listdir()
				holderList = []
				for elem in dirContents:
					isFile = os.path.isfile(elem)
					if isFile == True:
						holderList.append(str(elem))
				dirContents = holderList
				dirContents = sorted(dirContents, key=str.lower)
			# Note editing
			elif navigator =="e":
				userInput = int(input(" Enter the number of the note to edit: "))
				if 0 <= userInput < len(dirContents):
					editFile = dirContents[userInput]
					os.system(editor + " " + editFile)
					feedback = "Changes saved."
					clear()
				else:
					clear()
					feedback = "Note does not exist."
			elif navigator == "d":
				outOfNotes = False
				userInput = int(input(" Enter the number of the note to delete: "))
				if 0 <= userInput < len(dirContents):
					deleteFile = dirContents[userInput]
					confirmation = input("\x1b[33m" + " Are you sure you want to delete " + deleteFile + "? <y/N>" + "\x1b[0m").lower()
					if confirmation == "y":
						clear()
						os.remove(deleteFile)
						# Yes, these lines pop up several times. It's not a function because it breaks if I do that; it can be identical and have access to all variables and it still breaks. No clue why. I'm sure it'll click someday, or someone who knows more about Python will come up with a way to do it.
						dirContents = os.listdir()
						holderList = []
						for elem in dirContents:
							isFile = os.path.isfile(elem)
							if isFile == True:
								holderList.append(str(elem))
						dirContents = holderList
						dirContents = sorted(dirContents, key=str.lower)
						bottomPageNumber = 0
						topPageNumber = bottomPageNumber + fileCount
						pageCount = 1
						feedback = "Note deleted."
					else:
						clear()
						feedback = "Deletion canceled."
				else:
					clear()
					feedback = "Note does not exist."
			elif navigator == "q":
				clear()
				break
			# Any other cases that the user might manage to come up with.
			else:
				clear()
				feedback = "Invalid entry."

# Note menus and handling.
def noteHandler(workingDir):
	feedback = ""
	sharedSelection = "0"
	# Set settings
	settingsFile = os.environ['HOME'] + '/.pluralnotes' + "/" + username + "/data/settings.txt"
	settings = open(settingsFile, 'r').readlines()
	editor = settings[0].strip()
	fileCount = settings[1].strip()
	showDate = settings[2].strip()
	showUsername = settings[3].strip()
	clear()
	dirChanger(workingDir)
	while sharedSelection != "q":
		print()
		print(" You are here: " + workingDir)
		print(""" What would you like to do?
""")
		print("\x1b[31m" + " 1: Add a new note" + "\x1b[0m")
		print("\x1b[33m" + " 2: View, edit, or delete existing notes" + "\x1b[0m")
		print("\x1b[32m" + " q: Return to main menu" + "\x1b[0m")
		if feedback != "":
			print()
		print("\x1b[33m" + " " + feedback + "\x1b[0m")
		sharedSelection = input(" Enter selection: ").lower()

		if sharedSelection == "1" or sharedSelection == "a":
			feedback = ""
			newFile = input(" Enter note name: ")
			if newFile.isspace() == True or " " in newFile or "\n" in newFile or "\t" in newFile:
				clear()
				feedback = "Note names cannot contain spaces, tabs, or new lines. Please enter a valid note name."
			elif newFile == False or newFile == "":
				clear()
				feedback = "Please enter a note name."
			else:
				sharedDir = os.environ['HOME'] + '/.pluralnotes' + '/sharednotes'
				# Use settings to add date and/or username onto file
				if showDate.strip() == "True" or workingDir == sharedDir:
					newdatefile = newFile + "-" + str(todayDate)
					newFile = newdatefile
					sleep(0.05) # Filename improperly created if sleep is not added
				if showUsername.strip() == "True" or workingDir == sharedDir:
					newFile = newFile  + "-" + username
					sleep(0.05) # Filename improperly created if sleep is not added
				newFile = newFile + ".txt"
				clear()
				sleep(0.05) # Filename improperly created if sleep is not added
				os.system(editor + " " + newFile)
				# newFile = newFile  + "-" + username + "-" + todayDate + ".txt"
				# Sign note if requested by appending it onto the end of the file contents.
				print()
				signNameCheck = input(" Would you like to sign your note? <Y/n>").lower()
				if signNameCheck == "y" or signNameCheck == "yes":
					signName = open(newFile, "a")
					signName.write("\n -" + username) # New line helps keep the signature distinct
					signName.close
					clear()
					feedback = "Note signed!"
				else:
					clear()
					feedback = "Note saved!"
		elif sharedSelection == "2" or sharedSelection == "v" or sharedSelection == "e":
			feedback = ""
			# View or edit a note; paginated search
			clear()
			paginateDir(os.path.dirname)
		elif sharedSelection.lower() == "q" or sharedSelection.lower() == "quit" or sharedSelection.lower() == "b":
			# Back to main menu.
			feedback = ""
			clear()
			break
		else:
			clear()
			feedback = "Invalid entry. Please enter 1-5."

def replaceLine(fileName, lineNum, text):
    lines = open(fileName, 'r').readlines()
    lines[lineNum] = text
    out = open(fileName, 'w')
    out.writelines(lines)
    out.close()


dirChanger(notesDir) # Makes sure we aren't dumping notes all over the poor user's computer by moving into the designated PluralNotes directory (notesDir).
# Create other necessary directories within the main directory- one for archived notes of deleted users, and the other for notes that everyone can access.
if os.path.isdir(archiveDir) == False: os.mkdir(archiveDir)
if os.path.isdir(sharedDir) == False: os.mkdir(sharedDir)

clear()
print()
print("\x1b[32m" + " Welcome to Pluralnotes!" + "\x1b[0m")
print()

# Login sequence; tries to account for upper/lowercase and exits if the user requests it, else loops prompt until a valid login is entered. Allows users to create nonexistent username directories as long as they don't violate these restrictions, or log into an existing one.
login()
userDir = notesDir + "/" + username
# TODO: Check if a username including a backslash is a problem at all.
# TODO: Figure out password authentication and directory encryption so inter-user privacy is possible. This is meant to be a multiuser notekeeping utility on one shared computer account, so passwords are kind of important for that. Also MAKE SURE that the passwords are stored encrypted, and encrypt the entered password with the same hash to compare. People reuse passwords a lot and it's a security hazard to store them in plaintext. Make sure the password is not displayed as it's typed, too.

# Set settings from user file now that they're logged in.
settingsFile = os.environ['HOME'] + '/.pluralnotes' + "/" + username + "/data/settings.txt"
settings = open(settingsFile, 'r').readlines()
editor = settings[0]
fileCount = int(settings[1])
showDate = settings[2]
showUsername = settings[3]

clear() # Note: Clear is specified before the loop so that extra responses can be added before the prompt each time. Otherwise, clear just wipes them out. It takes more lines, but otherwise new responses don't show up before the loop like they should.

feedback = "" # Used to complain at users.
print()
print(" Welcome, " + username + "!")
action = 0
while 1:
	print()
	print(" What would you like to do?")
	print()
	print("\x1b[31m" + " 1: View personal notes" + "\x1b[0m")
	print("\x1b[33m" + " 2: View shared notes" + "\x1b[0m")
	print("\x1b[32m" + " 3. View archived notes" + "\x1b[0m")
	print("\x1b[36m" + " 4. Manage users" + "\x1b[0m")
	print("\x1b[34m" + " 5. Change settings" + "\x1b[0m")
	print("\x1b[35m" + " 6. Export notes" + "\x1b[0m")
	print("\x1b[31m" + " q: Quit" + "\x1b[0m")
	if feedback != "":
		print()
	print("\x1b[33m" + " " + feedback + "\x1b[0m")
	selection = input(" Enter selection: ")

	# Option 1: Enters personal directory and presents new options on what to do.
	if selection == "1":
		noteHandler(userDir)

# Enters shared directory and presents options.
	elif selection == "2":
		noteHandler(sharedDir)

	elif selection == "3":
		clear()
		dirChanger(archiveDir)
		paginateDir(archiveDir)

# Clear screen and present user management options.
	elif selection == "4":
		#clear()
		dirChanger(notesDir)
		sharedSelection = "0"
		while sharedSelection != "q":
			clear()
			print("""
 User Management
 What would you like to do?
""")
			print("\x1b[31m" + " 1: Add a user" + "\x1b[0m")
			print("\x1b[33m" + " 2: Rename a user" + "\x1b[0m")
			print("\x1b[32m" + " 3: View all users" + "\x1b[0m")
			print("\x1b[36m" + " 4: Delete a user" + "\x1b[0m")
			print("\x1b[34m" + " q: Return to main menu" + "\x1b[0m")
			if feedback != "":
				print()
			print("\x1b[33m" + " " + feedback + "\x1b[0m")
			sharedSelection = input(" Enter selection: ")

			if sharedSelection == "1":
				feedback = ""
				# Add a new user, with checks for disallowed names
				newUsername = input(" Enter name of new user: ")
				if os.path.isdir(notesDir + "/" + newUsername) == False:
					if newUsername.isspace() == True or " " in newUsername or "\n" in newUsername or "\t" in newUsername:
						clear()
						feedback = "Usernames cannot contain spaces, tabs, or new lines. Please enter a valid username."
					elif newUsername == False or newUsername == "":
						clear()
						feedback = "Please enter a valid username."
					# Disallow reserved shared directory name to avoid naming conflict
					elif newUsername == "sharednotes" or newUsername == "archives":
						clear()
						feedback = "Name reserved for shared notes or archives. Please enter a valid username."
					else:
						dirChanger(newUsername)
						if os.path.isdir("data") == False: os.mkdir("data")
						os.chdir(notesDir)
						clear()
						feedback = newUsername + " created."
				elif notesDir + "/" + newUsername == notesDir + "/":
					feedback = "Please enter a valid username."
				elif os.path.isdir(notesDir + "/" + newUsername) == True:
					feedback = "Could not create user; " + newUsername + " already exists!"
				else:
					feedback = "User could not be created or already exists."
			elif sharedSelection == "2":
				# Rename user by changing the name of their corresponding directory.
				renameDir = input(" Enter user to rename: ")
				if os.path.isdir(renameDir) == False:
					feedback = renameDir + " does not exist!"
				else:
					newName = input(" Enter " + renameDir + "'s new name: ")
					if newName.isspace() == True or " " in newName or "\n" in newName or "\t" in newName:
						clear()
						feedback = "Usernames cannot contain spaces, tabs, or new lines. Please enter a valid username."
					elif newName == False or newName == "":
						clear()
						feedback = "Please enter a valid username."
						# Disallow reserved shared directory name to avoid naming conflict
					elif newName == "sharednotes" or newName == "archives":
						clear()
						feedback = "Name reserved for shared notes or archives. Please enter a valid username."
					elif renameDir == newName:
						clear()
						feedback = renameDir + " already has this name!"
					elif os.path.isdir(newName) == True:
						clear()
						feedback = "This name is already taken!"
					else:
						confirmationCheck = input(" Are you sure you want to rename " + renameDir + " to " + newName + "? <Y/N>").lower()
						if confirmationCheck == "y":
							os.replace(renameDir, newName)
							if renameDir == username:
								username = newName
								userDir = notesDir + "/" + username
							clear()
							feedback = "Renaming successful; " + renameDir + " is now named " + newName + "."
						else:
							clear()
							feedback = "Cancelled renaming."
			elif sharedSelection == "3":
				feedback = ""
				clear()
				# View list of all users; do not allow opening directories, just viewing names and narrowing them down. Hide the shareduser and archive directory if possible. If possible, also display count of how many notes each user has in their directory. TODO: Find a way to merge this and the paginate function; the main difference is that the paginate function shows files and this needs to show directories.
				dirContents = os.listdir()
				dirContents = sorted(dirContents, key=str.lower)
				dirContentsLength = len(dirContents)
				selection = 0 # Used by user for input, and to break loop on request
				bottomPageNumber = 0 # Lower limit of a page
				pageCount = 1 # Which page we're on. Needs to be separate from bottomPageNumber because that variable increments by the number in fileCount, and page number increments by one.
				topPageNumber = bottomPageNumber + fileCount # Upper limit of a page.
				search = False
				while selection != "q":
					print()
					print(" Page " + str(pageCount))
					print()
					if len(dirContents) == 0:
						print(" No users here!")
						if feedback != "":
							print()
						print("\x1b[33m" + " " + feedback + "\x1b[0m")
						print(" Q: quit")
						print()
						navigator = input(" Enter selection: ").lower()
						if navigator == "q":
							feedback = ""
							clear()
							break
						else:
							clear()
							feedback = "Invalid entry."
					else:
						# Paginate users. Separate from regular pagination because users are directories, not files.
						for elem in dirContents[bottomPageNumber:topPageNumber]:
							isDir = os.path.isdir(elem)
							if isDir == True and elem != "archivednotes" and elem != "sharednotes":
								print(" " + str(elem))
						print()
						print("\x1b[31m" + " N: next page" + "\x1b[0m")
						print("\x1b[33m" + " B: previous page" + "\x1b[0m")
						print("\x1b[32m" + " S: search for users" + "\x1b[0m")
						if search == True:
							print("\x1b[36m" + " c: clear search" + "\x1b[0m")
						print("\x1b[35m" + " Q: quit" + "\x1b[0m")
						if feedback != "":
							print()
						print("\x1b[33m" + " " + feedback + "\x1b[0m")
						# User input time!
						selection = input(" Enter selection: ").lower()

						# Address running out of notes so the user can't iterate through empty pages
						if selection == "n" and dirContentsLength < topPageNumber + pageCount:
							clear()
							feedback = "No more users."
						elif selection == "b" and pageCount == 1:
							clear()
							# Fixes weird change in size of list that happens otherwise by resetting to page "one" (0)
							bottomPageNumber = 0
							topPageNumber = bottomPageNumber + fileCount
							pageCount = 1
							feedback = "You're already on the first page!"
							# Regular navigation
						elif selection == "n":
							feedback = ""
							clear()
							# Iterate to next page.
							bottomPageNumber = bottomPageNumber + fileCount
							topPageNumber = bottomPageNumber + fileCount
							pageCount = pageCount + 1
						elif selection == "b" and pageCount != 1:
							feedback = ""
							clear()
							# Iterate to previous page.
							bottomPageNumber = bottomPageNumber - fileCount
							topPageNumber = bottomPageNumber + fileCount
							pageCount = pageCount - 1
						# Address trying to change pages when there are no notes
						elif selection == "n" and len(dirContents[bottomPageNumber:topPageNumber]) == 0:
							feedback = ""
							clear()
						elif selection == "b" and len(dirContents[bottomPageNumber:topPageNumber]) == 0:
							feedback = ""
							clear()
						# Search function
						elif selection == "s":
							search = True
							feedback = ""
							regMatchList = []
							searchTerm = str(input(" Enter search term (regex): "))
							clear()
							pattern = re.compile(searchTerm)
							for elem in dirContents:
								match = re.search(pattern, elem)
								if match:
									regMatchList.append(elem)
							dirContents = sorted(regMatchList, key=str.lower)
							if dirContents == []:
								search = False
								clear()
								feedback = "No notes matching term found."
								dirContents = os.listdir()
								dirContents = sorted(dirContents, key=str.lower)
						elif selection == "c":
							clear()
							feedback = "Search cleared."
							search = False
							dirContents = os.listdir()
							holderList = []
							for elem in dirContents:
								isFile = os.path.isdir(elem)
								if isFile == True:
									holderList.append(str(elem))
							dirContents = holderList
							dirContents = sorted(dirContents, key=str.lower)
						elif selection == "q":
							feedback = ""
							clear()
							break
						# Any other cases that the user might manage to come up with.
						else:
							clear()
							feedback = "Invalid entry."

			elif sharedSelection == "4":
				# clear()
				# Delete a user. Gets confirmation twice to ensure the user doesn't delete someone they want to keep around, and moves their notes into the archive directory. Also accounts for trying to delete the current active user and disallows that. Requires exact case match to ensure mindful deletion.
				# TODO: if deleted user has a password, require that to be entered instead of their username in order to delete them. Should help prevent malicious deletion.
				# TODO: allow deletion of active user, return to login prompt if deleted.
				# TODO: Before moving deleted user's files, append their username to the end of the filename (or the end of the note) so that archives are more clear.
				deleteUsername = input(" Enter user to delete, or q to cancel: ")
				deleteFolder = notesDir + "/" + deleteUsername
				if os.path.isdir(deleteFolder) == False:
					clear()
					print()
					feedback = "Cannot delete nonexistent users."
				else:
					print("\x1b[31m" + " Deleting " + deleteUsername + " will move all their notes into archives." + "\x1b[0m")
					confirmationCheck = input(" Enter username again to confirm deletion, or q to cancel: ")

					if deleteUsername == username:
						print()
						feedback = "Cannot delete active user."
					elif deleteUsername != confirmationCheck:
						print()
						feedback = "Usernames do not match. Check spelling and capitalization."
					elif deleteUsername.lower() == "q" or confirmationCheck.lower() == "q":
						print()
						feedback = "Deletion cancelled."
					elif os.path.isdir(deleteFolder) == False:
						print()
						feedback = "Cannot delete nonexistent users."
					elif deleteUsername == confirmationCheck:
						archiveList = os.listdir(path=notesDir + "/" + deleteUsername)
						archiveFilename = "0"
						if archiveList != []:
							for elem in archiveList:
								if elem != "data":
									originalName = notesDir + "/" + deleteUsername + "/" + elem
									archiveFilename = str(elem[:-4]) + "-" + deleteUsername + ".txt"
									os.rename(originalName, archiveFilename)
									shutil.move(archiveFilename, archiveDir)
							shutil.rmtree(deleteFolder)
							clear()
						print()
						feedback = deleteUsername + " successfully deleted. Their notes can now be found in the archives."
					else:
						clear()
						feedback = "Cannot delete " + deleteUsername + ". Did you spell their name correctly?"

			elif sharedSelection == "5" or sharedSelection.lower() == "q" or sharedSelection.lower() == "quit":
				feedback = ""
				clear()
				break
			else:
				clear()
				feedback = "Invalid entry. Please enter 1-5."

	elif selection == "5":
		feedback = ""
		action = 0
		clear()
		while action != "q":
			settingsFile = userDir + "/data/settings.txt"
			if os.path.isfile(settingsFile) == False:
				f = open(notesDir + "/" + username + "/data/settings.txt", "a")
				f.write("vim" + "\n")
				f.write("10" + "\n")
				f.write("True" + "\n")
				f.write("False" + "\n")
				f.write("-" + "\n")
				f.write("Warning: Do not edit spacing!" + "\n")
				f.write("If manually editing settings, True/False must be capitalized. If you mess it up, don't worry- you can either delete this file (the program will remake it) or reset to the default in settings.")
				f.write("""Settings in order:
				Editor
				Page size
				Include date in new note names
				Include username in new note names""")
			f = open(settingsFile, "r")
			print()
			print(" Settings:")
			print()
			print("\x1b[31m" + " 1. Editor = " + f.readline().strip() + "\x1b[0m")
			print("\x1b[33m" + " 2. Page size = " + f.readline().strip() + "\x1b[0m")
			print("\x1b[32m" + " 3. Include date in note names = " + f.readline().strip() + "\x1b[0m")
			print("\x1b[36m" + " 4. Include username in note names = " + f.readline().strip() + "\x1b[0m")
			print("\x1b[34m" + " r: Reset settings to defaults." + "\x1b[0m")
			print("\x1b[35m" + " q: Back to main menu." + "\x1b[0m")
			if feedback != "":
				print()
			print("\x1b[33m" + " " + feedback + "\x1b[0m")
			action = input(" Enter selection: ").lower()
			if action == "q" or action == "quit":
				clear()
				selection = 0
				feedback = ""
				break
			if action == "1":
				newEditor = str(input("Enter the command for your preferred editor: ")).lower()
				editor = newEditor
				newEditor = newEditor + " \n"
				replaceLine(settingsFile, 0, newEditor)
				feedback = ""
				clear()
			if action == "2":
				newPageSize = str(input("Enter how many entries you'd like per page: ")).lower()
				numberCheck = str.isdigit(newPageSize)
				if numberCheck == True:
					fileCount = newPageSize
					newPageSize = newPageSize + "\n"
					replaceLine(settingsFile, 1, newPageSize)
					feedback = ""
					clear()
				else:
					clear()
					feedback = "Must enter a number from 0-99."
			if action == "3":
				feedback = ""
				clear()
				if showDate == "True\n" or showDate == "True":
					newShowDate = "False" + "\n" # Using showDate would mess things up because of the new line. Not the best, I know, but it works.
				else:
					newShowDate = "True" + "\n"
				replaceLine(settingsFile, 2, newShowDate)
				showDate = newShowDate
			if action == "4":
				if showUsername == "True\n" or showUsername == "True":
					newShowUsername = "False" + "\n" # Using showDate would mess things up because of the new line. Not the best, I know, but it works.
				else:
					newShowUsername = "True" + "\n"
				replaceLine(settingsFile, 3, newShowUsername)
				showUsername = newShowUsername
				feedback = ""
				clear()
			if action == "r":
				# Recreates original settings.
				replaceLine(settingsFile, 0, "vim\n")
				replaceLine(settingsFile, 1, "10\n")
				replaceLine(settingsFile, 2, "True\n")
				replaceLine(settingsFile, 3, "True\n")
				feedback = ""
				clear()

	elif selection == "6":
		clear()
		# Copy detection- if pluralnotes.zip already exists, check if pluralnotes1.zip exists, then pluralnotes2.zip, and so on until a free name is found. Then make that file and chuck it in the home directory for the user.
		copyNumber = 1
		if os.path.exists(os.environ['HOME'] + "/pluralnotes.zip") == True or os.path.exists(os.environ['HOME'] + "\pluralnotes.zip") == True:
			while os.path.exists(os.environ['HOME'] + "/pluralnotes" + str(copyNumber) + ".zip") == True or os.path.exists(os.environ['HOME'] + "/pluralnotes" + str(copyNumber) + ".zip") == True:
				copyNumber = copyNumber + 1
			zipName = "pluralnotes" + str(copyNumber)
		else:
			zipName = "pluralnotes"
		os.chdir(os.environ['HOME'])
		shutil.make_archive(zipName, 'zip', root_dir=notesDir)
		#shutil.move(zipName + ".zip", os.environ['HOME'])
		os.chdir(notesDir)
		feedback = zipName + ".zip created; it can be found in your home directory."

	elif selection == "7" or selection.lower() == "q" or selection.lower() == "quit":
		quitNotes = True
		# Clear the terminal to keep things looking clean.
		clear()
		print("See you next time, " + username + "!")
		sys.exit(0)
# Dealing with edge cases where nonexistent options are entered.
	else:
		clear()
		feedback = "Invalid entry. Please select 1-6."
