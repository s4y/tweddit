import pycurl, json, secrets

STREAM_URL = "https://stream.twitter.com/1/statuses/sample.json"

urls = {}

class Client:
	def __init__(self):
		self.buffer = ""
		self.conn = pycurl.Curl()
		self.conn.setopt(pycurl.USERPWD, "%s:%s" % (secrets.username, secrets.password))
		self.conn.setopt(pycurl.URL, STREAM_URL)
		self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
		self.conn.perform()

	def on_receive(self, data):
		import operator
		import datetime
		self.buffer += data
		if data.endswith("\r\n") and self.buffer.strip():
			content = json.loads(self.buffer)
			self.buffer = ""

			if 'entities' in content:
				tweet_urls = [url['expanded_url'] or url['url'] for url in content['entities']['urls']]
				for k, url in enumerate(tweet_urls):
					urls[url] = ((urls[url][0] + 1 if (url in urls) else 1), datetime.datetime.now())
					print '%d: %s (total: %d)' % (urls[url][0], url, len(urls))
				if len(urls) > 15000:
					urls_sorted = urls.items()
					urls_sorted.sort(key=operator.itemgetter(1), reverse=True)
					urls_sorted.sort(reverse=True)
					for url_to_delete in urls_sorted[10000:]:
						del urls[str(url_to_delete[0])]
		if len(urls) % 50 == 0:
				urls_sorted = urls.items()
				urls_sorted.sort(key=operator.itemgetter(1), reverse=True)
				print '\n-------------\n\n\n'
				for url in urls_sorted[:10]:
					print '%d: %s' % (url[1][0], url[0])
				print '\n\n'

client = Client()
