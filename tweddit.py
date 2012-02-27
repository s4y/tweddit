import secrets, threading
from runloop import RunLoop
from operator import itemgetter

STREAM_URL = "https://stream.twitter.com/1/statuses/sample.json"

class TweetStream(threading.Thread):
	def __init__(self, handler):
		import pycurl
		self.buffer = ""
		self.handler = handler
		self.conn = pycurl.Curl()
		self.conn.setopt(pycurl.USERPWD, "%s:%s" % (secrets.username, secrets.password))
		self.conn.setopt(pycurl.HEADER, 0)
		self.conn.setopt(pycurl.NOSIGNAL, 1)
		self.conn.setopt(pycurl.URL, STREAM_URL)
		self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
		threading.Thread.__init__(self)
		self.daemon = True
	def run(self):
		self.conn.perform()
	def on_receive(self, data):
		from json import loads
		self.buffer += data
		if data.endswith("\r\n") and self.buffer.strip():
			self.handler(loads(self.buffer))
			self.buffer = ""

class Tweddit():
	def __init__(self):
		from sqlite3 import connect
		self.conn = connect('tweddit')
		self.cursor = self.conn.cursor()
		self.cursor.execute('CREATE TABLE IF NOT EXISTS tweet_urls(url TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
	def handle_tweet(self, tweet):
		from datetime import datetime
		if 'entities' in tweet:
			for url in [url['expanded_url'] or url['url'] for url in tweet['entities']['urls']]:
				self.cursor.execute('INSERT INTO tweet_urls ("url") VALUES(?)', (url,))
				self.conn.commit()
				print url

if __name__ == '__main__':
	import sqlite3
	conn = sqlite3.connect('tweddit')
	conn.row_factory = sqlite3.Row
	run_loop = RunLoop()
	tweddit = Tweddit()
	stream = TweetStream(run_loop.onLoop(tweddit.handle_tweet))
	def status():
		cursor = conn.cursor()
		cursor.execute('SELECT COUNT(*) AS count FROM tweet_urls')
		print '\n-------------'
		print 'Total tweeted URLS: %d' % cursor.fetchone()['count']
		print ''
		cursor.execute('SELECT url, COUNT(*) AS COUNT FROM tweet_urls GROUP BY url ORDER BY count DESC LIMIT 0, 10')
		for url in cursor:
			print '%d: %s' % (url['count'], url['url'])
		print ''
		cursor.close()
	run_loop.every(status, 5)
	stream.start()
	run_loop.run()
