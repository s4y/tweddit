import secrets, threading
from operator import itemgetter

STREAM_URL = "https://stream.twitter.com/1/statuses/sample.json"



class TwitterClient(threading.Thread):
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
		self.urls = {}
		self.client = TwitterClient(self.handle_tweet)
	def start(self):
		self.client.start();
	def handle_tweet(self, tweet):
		from datetime import datetime
		if 'entities' in tweet:
			tweet_urls = [url['expanded_url'] or url['url'] for url in tweet['entities']['urls']]
			for url in tweet_urls:
				self.urls[url] = ((self.urls[url][0] + 1 if (url in self.urls) else 1), datetime.now())
				print '%d: %s (total: %d)' % (self.urls[url][0], url, len(self.urls))
			if len(self.urls) > 15000:
				self.prune()
	def prune(self):
		urls_sorted = self.urls.items()
		urls_sorted.sort(key=itemgetter(1), reverse=True)
		urls_sorted.sort(reverse=True)
		for url_to_delete in urls_sorted[10000:]:
			del self.urls[str(url_to_delete[0])]

if __name__ == '__main__':
	tweddit = Tweddit()
	tweddit.start()
	e = threading.Event()
	while True:
		e.wait(10)
		urls_sorted = tweddit.urls.items()
		urls_sorted.sort(key=itemgetter(1), reverse=True)
		print '\n-------------\n\n\n'
		for url in urls_sorted[:10]:
			print '%d: %s' % (url[1][0], url[0])
		print '\n\n'
