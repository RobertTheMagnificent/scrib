from plugins import ScribPlugin
import imaplib
import email

# User Alias and Command
email_alias = "!email"
command = { "email": "Usage: !email\nIf setup, check bot's e-mail and feed it the contents of every e-mail's body." }

class EmailPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		if command_list[0] == email_alias and len(command_list)==1:
			msg = "Checking my e-mail!"
			check_email()
		else:
			msg = "No e-mail to check."
		return msg

	def extract_body(payload):
		if isinstance(payload,str):
			return payload
		else:
			return '\n'.join([extract_body(part.get_payload()) for part in payload])

	email_user = ''
	email_password = ''

	conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
	conn.login( email_user , email_password )
	conn.select()
	typ, data = conn.search(None, 'UNSEEN')

	def check_email():
		try:
			for num in data[0].split():
				typ, msg_data = conn.fetch(num, '(RFC822)')
				for response_part in msg_data:
					if isinstance(response_part, tuple):
						msg = email.message_from_string(response_part[1])
						subject=msg['subject']
						scrib.barf(scrib.DBG, "%s\033[0m" % subject)
						print(subject)
						payload=msg.get_payload()
						body=extract_body(payload)
						print(body)
				typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
		finally:
			try:
				conn.close()
			except:
				pass
			conn.logout()

ScribPlugin.addPlugin( command, email_alias, EmailPlugin() )