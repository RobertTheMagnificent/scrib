from plugins import ScribPlugin

def sendMessage( event, text, scrib ):
	if ScribPlugin.process_table[event] != '':
		return ScribPlugin.process_table[event].action(text, scrib)
	else:
		return ''

def reloadPlugin( event ):
	if ScribPlugin.process_table[event] != '':
		reload(event)
	else:
		return 'Reloading error'