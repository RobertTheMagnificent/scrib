froms import ScribPlugin

def sendMessage( event, text ):
	if ScribPlugin.process_table[event] != '':
		return ScribPlugin.process_table[event].action(text)
	else:
		return ''
