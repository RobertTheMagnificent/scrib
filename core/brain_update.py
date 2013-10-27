#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrib import *

class scrib(self):
	def _init__(self):
		self.settings = self.cfgfile.cfgset()
		self.settings.load("../conf/scrib.cfg",
						   {"max_words": ("max limits in the number of words known", 6000),
							"learning": ("Allow the bot to learn", 1),
							"ignore_list": ("Words that can be ignored for the answer", ['!.', '?.', "'", ',', ';']),
							"censored": ("Don't learn the sentence if one of those words is found", []),
							"num_aliases": ("Total of aliases known", 0),
							"aliases": ("A list of similars words", {}),
							"pubsym": ("Symbol to append to cmd msgs in public", "!"),
							"no_save": ("If True, Scrib doesn't save his brain and configuration to disk", "False")
						   })

		if self.settings.debug == 1:
			barf(DBG, "Class scrib initialized.")

		# Read the brain
		barf(SAV, "Reading my brain...")
		try:
			zfile = zipfile.ZipFile('../brain/cortex.zip', 'r')
			for filename in zfile.namelist():
				data = zfile.read(filename)
				file = open(filename, 'w+b')
				file.write(data)
				file.close()
		except (EOFError, IOError), e:
			barf(ERR, "No brain found, or perhaps corrupt? Recreating.")
		try:
			f = open("../brain/version", "rb")
			s = f.read()
			f.close()
			if s != self.version.brain:
				barf(ERR, "Brain version incorrect.")
				found_ver = "UNKOWN"
				ancient = "0.0.1"
				old = "0.1.0"

				if s == ancient:
					found_ver = ancient
				if s == old:
					found_ver = old

				if s == found_ver:
					barf(ACT, "Brain version %s detected. Attempting update..." % found_ver)
					f = open("../brain/words.dat", "rb")
					s = f.read()
					f.close()
					self.words = marshal.load(s)

					f = open("../brain/lines.dat", "rb")
					s = f.read()
					f.close()
					self.lines = marshal.load(s)

					f = open("../brain/version" "w")
					f.write(self.version.brain)
					f.close()

					barf(ACT, "Brain update a success!")
				else:
					barf(ERR, "Unable to update this brain.")
					sys.exit(1)
			elif found_ver == "UNKNOWN":
				barf(ERR, "Unknown brain version. Cannot proceed.")
				sys.exit(1)
		except (EOFError, IOError), e:
			barf(ERR, "Could not update brain. :(")
			sys.exit(1)
		self.save_all(False)

	def save_all(self, restart_timer=True):
		if self.settings.no_save != "True":
			nozip = "no"
			barf(SAV, "Writing to my brain...\033[0m")

			try:
				zfile = zipfile.ZipFile('../brain/cortex.zip', 'r')
				for filename in zfile.namelist():
					data = zfile.read(filename)
					file = open(filename, 'w+b')
					file.write(data)
					file.close()
				if self.settings.debug == 1:
					barf(DBG, "Cortex saved.")
			except:
				barf(ERR, "No brain found, or it's broken. Attempting to restore...")
				try:
					os.remove('../brain/cortex.zip')
				except:
					pass

			f = open("../brain/words.dat", "wb")
			s = pickle.dumps(self.words)
			f.write(s)
			f.close()
			if self.settings.debug == 1:
				barf(DBG, "Words saved.")
			f = open("../brain/lines.dat", "wb")
			s = pickle.dumps(self.lines)
			f.write(s)
			f.close()
			if self.settings.debug == 1:
				barf(DBG, "Lines saved.")

			#save the version
			f = open("../brain/version", "w")
			f.write(self.version.brain)
			f.close()
			if self.settings.debug == 1:
				barf(DBG, "Version saved.")

			#zip the files
			f = zipfile.ZipFile('../brain/cortex.zip', 'w', zipfile.ZIP_DEFLATED)
			f.write('../brain/words.dat')
			if self.settings.debug == 1:
				barf(DBG, "Words zipped")
			f.write('../brain/lines.dat')
			if self.settings.debug == 1:
				barf(DBG, "Lines zipped")
			try:
				f.write('../brain/version')
				if self.settings.debug == 1:
					barf(DBG, "Version zipped")
			except:
				f2 = open("../brain/version", "w")
				f2 = write(self.version.brain)
				f.write('../brain/version')
				if self.settings.debug == 1:
					barf(DBG, "Version written.")
			f.close()

			f = open("../brain/words.dat", "w")
			# write each words known
			wordlist = []
			#Sort the list before to export
			for key in self.words.keys():
				try:
					wordlist.append([key, len(self.words[key])])
				except:
					pass
			wordlist.sort(lambda x, y: cmp(x[1], y[1]))
			map((lambda x: f.write(str(x[0]) + "\n\r") ), wordlist)
			f.close()
			if self.settings.debug == 1:
				barf(DBG, "Words written.")

			f = open("../brain/sentences.dat", "w")
			# write each words known
			wordlist = []
			#Sort the list before to export
			for key in self.unfilterd.keys():
				wordlist.append([key, self.unfilterd[key]])
			wordlist.sort(lambda x, y: cmp(y[1], x[1]))
			map((lambda x: f.write(str(x[0]) + "\n") ), wordlist)
			f.close()
			if self.settings.debug == 1:
				barf(DBG, "Sentences written.")

			if restart_timer is True:
				self.autosave = threading.Timer(to_sec("125m"), self.save_all)
				self.autosave.start()
				if self.settings.debug == 1:
					barf(DBG, "Restart timer started.")

			# Save settings
			self.settings.save()
			self.brainstats.save()
			self.version.save()

			barf(SAV, "Brain saved.")

if __name__ == "main":
	my_scrib = scrib.scrib()
	my_scrib.save_all(False)
	del my_scrib