from plugins import ScribPlugin
import imaplib
import email

email_user = ''
email_password = ''

#ScribPlugin.scrib.barf(ScribPlugin.scrib.DBG, "Logging in as \033[0m%s" % email_user)

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)

conn.login(email_user, email_password)
conn.select()
typ, data = conn.search(None, 'UNSEEN')


def extract_body(payload):
	if isinstance(payload, str):
		return payload
	else:
		return '\n'.join([extract_body(part.get_payload()) for part in payload])


def checkemail():
	try:
		for num in data[0].split():
			typ, msg_data = conn.fetch(num, '(RFC822)')
			for response_part in msg_data:
				if isinstance(response_part, tuple):
					mail = email.message_from_string(response_part[1])
					subject = mail['subject']
					#ScribPlugin.scrib.barf(ScribPlugin.scrib.DBG, "%s\033[0m" % subject)
					print(subject)
					payload = mail.get_payload()
					body = extract_body(payload)
					#ScribPlugin.scrib.barf(ScribPlugin.scrib.DBG, "%s\033[0m" % body)
					print(body)
			typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
	finally:
		try:
			conn.close()
		except:
			pass
		conn.logout()

# User Alias and Command
alias = "!email"
command = {"email": "Usage: !email\nIf setup, check bot's e-mail and feed it the contents of every e-mail's body."}

class EmailPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		msg = ""
		if command_list[0] == alias:
			msg = "Checking my e-mail!"
			try:
				checkemail()
			except:
				msg = "Checking e-mail failed."
		return msg


ScribPlugin.addPlugin(command, alias, EmailPlugin())