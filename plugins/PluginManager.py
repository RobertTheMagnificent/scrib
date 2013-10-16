from plugins import TestPlugin

def sendMessage( event, text ):
	if TestPlugin.process_table[event] != '':
		return TestPlugin.process_table[event].action(text)
	else:
		return ''
