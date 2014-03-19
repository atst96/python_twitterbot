#!/usr/local/bin/python
# -*- coding:utf-8 -*-

from tweepy import OAuthHandler, Stream, StreamListener, TweepError, API
import logging, sys, urllib, re, datetime

reset = u""; #update_name reset で使用する表示名
screen_name = ""
user_id = 0



# 設定
tokens = {
	"ConsumerKey" 		: "ConsumerKey",
	"ConsumerSecret" 	: "ConsumerSecret",
	"AccessToken" 		: "AccessToken",
	"AccessTokenSecret" : "AccessTokenSecret",
}

auth = OAuthHandler(tokens["ConsumerKey"], tokens["ConsumerSecret"])
auth.set_access_token(tokens["AccessToken"], tokens["AccessTokenSecret"])

class UserStream(Stream):
	def user_stream(self, follow=None, track=None, async=False, locations=None):
		self.parameters = {"delimited": "length" }
		self.headers['Content-type'] = "application/x-www-form-urlencoded"
		if self.running:
			raise TweepError('Stream object already connected!')
		self.scheme = "https"
		self.host = 'userstream.twitter.com'
		self.url = '/1.1/user.json'
		if follow:
			self.parameters['follow'] = ','.join(map(str, follow))
		if track:
			self.parameters['track'] = ','.join(map(str, track))
		if locations and len(locations) > 0:
			assert len(locations) % 4 == 0
			self.parameters['locations'] = ','.join(['%.2f' % l for l in locations])
		self.body = urllib.urlencode(self.parameters)
		logging.debug("[ User Stream URL ]: %s://%s%s" % (self.scheme, self.host, self.url))
		logging.debug("[ Request Body ] :" + self.body)
		self._start(async)
		print "Update name bot started !!!"

	
class _StreamListener(StreamListener):
	def on_status(self, status):
		try:
			#print '@' + status.user.screen_name + ': ' + status.text; print
			m = re.match(r"^@{0}\s*([0-9a-zA-Z_]*)\s*(.*?)$".format(screen_name), status.text)
			r = re.match(r"^(.*?)\(@{0}\)$".format(screen_name), status.text)
			if m != None:
				s2 = m.group(1); s3 = m.group(2)
				print "Received Command %s" % s2
				if s2 == "update_name":
					if s3 == "reset":
						if API(auth).update_profile(name=reset) != None:
							API(auth).update_status(u"Success Name Reset." + attime(), status.id)
						else:
							API(auth).update_status(u"Failed Name Reset..." + attime(), status.id)
					else:
						if len(s3) > 20:
							print "Update_name over length"
							API(auth).update_status(u".@{0} 文字数オーバーです！＞.＜@✌({1}/20文字) {2}".format(status.user.screen_name, len(s3), attime()), status.id);
						else:
							if API(auth).update_profile(name=s3) != None:
								print "Success update_name %s" % s3
								API(auth).update_status(u".@{0} さんが「{1}」に改名させました。 {2}".format(status.user.screen_name, s3, attime()), status.id);
							else:
								print "Failed update_name %s" % s3
								API(auth).update_status(u".@{0} さんが「{1}」に改名させることができませんでした。 {2}".format(status.user.screen_name, s3, attime()), status.id);
				elif s2 == "say":
					if(API(auth).update_status(s3)):
						print "Success Update @{0}".format(s3)
					else:
						print "Failed Update @{0}".format(s3)
			elif r != None:
				s1 = r.group(1);
				if len(s1) > 20:
					print "Update_name over length"
					API(auth).update_status(u".@{0} 文字数オーバーです！＞.＜@✌({1}/20文字) {2}".format(status.user.screen_name, len(s1), attime()), status.id);
				else:
					if API(auth).update_profile(name=s1) != None:
						print "Success update_name %s" % s1
						API(auth).update_status(u".@{0} さんが「{1}」に改名させました。 {2}".format(status.user.screen_name, s1, attime()), status.id);
					else:
						print "Failed update_name %s" % s1
						API(auth).update_status(u".@{0} さんが「{1}」に改名させました。 {2}".format(status.user.screen_name, s1, attime()), status.id);
		except tweepy.error.TweepError, e:
			pass
		except:
			print
			print "Error : "
			print sys.exc_info()
			print
			pass
		
def post(c):
	API(auth).update_status(c)

def attime():
	return "at {0}".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
	
if __name__ == '__main__':
	info =  API(auth).verify_credentials()
	screen_name = info.screen_name; user_id = info.id
	
	stream = UserStream(auth, _StreamListener(api=API(auth_handler=auth)))
	stream.timeout = None
	
	stream.user_stream()

	var = raw_input("Exit...")
