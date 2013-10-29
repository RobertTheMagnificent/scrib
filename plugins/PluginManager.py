from plugins import ScribPlugin

def sendMessage( event, text, scrib, c ):
	if ScribPlugin.process_table[event] != '':
		return "%s %s" % (scrib.settings.pubsym, ScribPlugin.process_table[event].action(text, scrib, c))
	else:
		return ''

def reloadPlugin( event ):
	if ScribPlugin.process_table[event] != '':
		reload(event)
		return "Reloaded %s" % event
	else:
		return 'Reloading error'