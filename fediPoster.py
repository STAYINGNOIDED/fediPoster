import requests, argparse
import os, sys, json

parser = argparse.ArgumentParser()
parser.add_argument("-s", metavar="status",     type=str, help="what you want to post", nargs=1)
parser.add_argument("-c", metavar="subject",    type=str, help="subject field",         nargs=1)
# Will add functionality for multiple attachments by August 2021
parser.add_argument("-a", metavar="attachment(s)",        help="path(s) to attachment(s)",    nargs="+")
parser.add_argument("-i", metavar="instance",   type=str, help="instance url without https:// prefix,, eg; <sleepy.cafe>", nargs=1)
parser.add_argument("-u", metavar="un/pw",      type=str, help="username and password, format like <username:password>",   nargs=1, default="default")
parser.add_argument("-t", metavar="token",      type=str, help="bearer token,, generate here: https://tinysubversions.com/notes/mastodon-bot/", nargs=1)
parser.add_argument("-f", metavar="format",     type=str, help="format,, plain/markdown/html/bbcode", nargs="?", default="plain")
parser.add_argument("-v", metavar="visibility",           help="visibility", nargs="?", default="public")
args = parser.parse_args()
d = vars(args)

status     = d["s"][0]
if d["c"]:
	subject    = d["c"][0]
else: subject = ""
instance   = d["i"][0]
auth       = d["u"][0]
token      = d["t"][0]
format     = "text/" + d["f"]
visibility = d["v"]
if d["a"]:
	attach = []
	for i in d["a"]:
		attach.append( os.path.join( sys.path[0], i ) )

# Posts using your user name and password.
# Takes the text you want posted, the instance, visibility,
# format (markdown html plaintext bbcode), username and
# password. Not recommended and not used in this program.
def doPost( txt, sub, inst, vis, form, un, pw ):
	data = {
	'status':       txt,
	'visibility':   vis,
	'content_type': form,
	'spoiler_text': sub    }

	response = requests.post( "https://" + inst + "/api/v1/statuses", data=data, auth=(un, pw) )

# Same as doPost but takes a token in place of your
# username and password. Can be generated here: 
# https://tinysubversions.com/notes/mastodon-bot/
def doPostOAuth( txt, sub, inst, vis, form, tok ):
	headers = {
	"Authorization":"Bearer " + tok   }
	
	data = {
	'status':       txt,
	'visibility':   vis,
	'content_type': form,
	'spoiler_text': sub    }

	response = requests.post("https://" + inst + "/api/v1/statuses", headers=headers, data=data)
	
# Uploads an attachment or attachments to the server 
# and returns media ID(s).	
def getMediaIDOAuth( img, inst, tok ):
	ids = []
	for i in img:
		files   = {
		"file": (i, open(i, 'rb')), }
		headers = {
		"Authorization":"Bearer " + tok }

		response = requests.post("https://" + inst + "/api/v1/media", headers=headers, files=files)
		content  = response.content
		a        = json.loads(content)
		ids.append( a["id"] )
	
	return ids

# Calls the getMediaIDOAuth script for you and 
# uses it to post your attachment(s). 
def doImageOAuth( txt, sub, img, inst, vis, form, tok ):
	id = getMediaIDOAuth(img, inst, tok)
	
	headers = {
	"Authorization":"Bearer " + tok    }
	
	data = {
	'media_ids[]':  id,
	'status':       txt,
	'visibility':   vis,
	'content_type': form,
	'spoiler_text': sub    }
	
	response = requests.post("https://" + inst + "/api/v1/statuses", headers=headers, data=data)

if d["a"]:
	doImageOAuth( status, subject, attach, instance, visibility, format, token )
else:
	doPostOAuth( status, subject,          instance, visibility, format, token )
