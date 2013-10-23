# -*- coding: utf-8 -*-
#
# scrib config file

import string
import time

def _load_config(filename):
	"""
  Load a configuration that returns variables.
	"""
	try:
		f = open(filename, "r")
	except IOError, e:
		return None

	stuff = {}
	line = 0

	while 1:
		line = line + 1
		s = f.readline()
		if s=="":
			break
		if s[0]=="#":
			continue
			
		while s.find("#") == -1:
			lecture = f.readline()
			if lecture == "":
				break
    
			if s[-2] == '\\':
				s = s[:-2]
    
			s = s[:s.rfind("\n")] + lecture
			line = line + 1

		s = string.split(s, "=")
		try:
			stuff[string.strip(s[0])] = eval(string.strip(string.join(s[1:], "=")))
		except:
			print "[%s][!] Malformed line in %s line %d" % (get_time(), filename, line)
			print "[%s][!] \t%s" % (get_time(), s)
			continue
	return stuff
		
def _save_config(filename, fields):
	"""
  Should be a dictionary;
  Keys as names of variables containing tuple.
	"""
	f = open(filename, "w")

	for key in fields.keys():
		f.write("# "+fields[key][0]+" #\n")
		s = repr(fields[key][1])
		f.write(key+"\t= ")

		#Create newline after each entry
		if s.find("],") != -1:
			cut_string = ""
			while s.find("],") != -1:
				position = s.find("],")+3
				cut_string = cut_string + s[:position] + "\n\t"
				s = s[position:]
			s = cut_string + s
			f.write(s+"\n")
			continue

		#cut at 80 col
		if len(s) > 80:
			cut_string = ""
			while len(s) > 80:
				position = s.rfind(",",0,80)+1
				cut_string = cut_string + s[:position] + "\n\t\t"
				s = s[position:]
			s = cut_string + s
		f.write(s+"\n")

	f.write("# End of configuration #")
	f.close()


class cfgset:
	def load(self, filename, defaults):
		"""
		Defaults should be key=variable name, value=
		tuple of (comment, default value)
		"""
		self._defaults = defaults
		self._filename = filename

		for i in defaults.keys():
			self.__dict__[i] = defaults[i][1]

		# try to laad saved ones
		vars = _load_config(filename)
		if vars == None:
			# none found. this is new
			self.save()
			return
		for i in vars.keys():
			self.__dict__[i] = vars[i]

	def save(self):
		"""
		Save borg settings
		"""
		keys = {}
		for i in self.__dict__.keys():
			# reserved
			if i == "_defaults" or i == "_filename":
				continue
			if self._defaults.has_key(i):
				comment = self._defaults[i][0]
			else:
				comment = ""
			keys[i] = (comment, self.__dict__[i])
		# save to config file
		_save_config(self._filename, keys)

