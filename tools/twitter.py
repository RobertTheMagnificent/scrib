#!/usr/bin/env python

import sys
from twyt import twitter, data

t = twitter.Twitter()
# t.set_auth("twitter", "password")
t.set_auth("", "")
tweet = sys.argv[1]

return_val = t.status_update(tweet)
print 'I tweeted: %s' % tweet
