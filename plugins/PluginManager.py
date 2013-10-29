from plugins import ScribPlugin

def sendMessage( event, text, scrib, c ):
	if ScribPlugin.process_table[event] != '':
		return "%s %s" % (scrib.settings.pubsym, ScribPlugin.process_table[event].action(text, scrib, c))
	else:
		return '%s Nothing to return.' % scrib.settings.pubsym

def reloadPlugin( event ):
	if ScribPlugin.process_table[event] != '':
		reload(event)
		return "%s Reloaded %s" % (scrib.settings.pubsym, event)
	else:
		return '%s Reloading error' % scrib.settings.pubsym