from plugins import ScribPlugin
import cfgfile
import twitter

# User Alias and Command
alias = "!tweet"
command = { "tweet": "Owner Command. Usage: !tweet\nTweet the most recently said line." }

# Plugin Action
class TwitterPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == alias and scrib.settings.twitter == 1:
			self.settings = cfgfile.cfgset()
			self.settings.load("conf/twitter.cfg",
			{ "con_key = ": ("Consumer Key", ""),
			  "con_secret": ("Consumer Secret", ""),
			  "token_key":	("Access Token", ""),
			  "token_secret":("Access Secret", "")
			} )
			scrib_auth = twitter.OAuth(token_key, token_seret, con_key, con_secret)
			twit = twitter.Twitter(auth=scrib_auth)

ScribPlugin.addPlugin( command, alias, TwitterPlugin() )
