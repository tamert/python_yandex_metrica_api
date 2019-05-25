#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import getopt
import requests
import json
import datetime
from fcache.cache import FileCache

mycache = FileCache('yandex')

# variables
YANDEX_ID = "XXX"
YANDEX_PASS = "XXX"
YANDEX_CODE = False
YANDEX_REQUEST = {'content-type': 'application/x-www-form-urlencoded'}

# @todo: is null variabble get on the database
MY_SLUG = 'login'
ALL = False

argv = sys.argv[1:]


if argv==['-g', 'all'] or argv==['-get', 'all']:
	ALL = True
else:

	try:
		opts, args = getopt.getopt(argv, "hi:o:", ["code=", "slug="])
	except getopt.GetoptError:
		print('Error-Used:')
		print('main.py -o <slug>')
		print('main.py -g all')
		print('main.py -i <code>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('Used:')
			print('main.py -o <slug>')
			print('main.py -g all')
			print('main.py -i <code>')
			sys.exit()
		elif opt in ("-i", "--code"):
			YANDEX_CODE = arg
		elif opt in ("-o", "--slug"):
			MY_SLUG = arg


		
# start
if "access_token" not in mycache.keys() or not YANDEX_CODE==False:

	query = {'grant_type': 'authorization_code','code': YANDEX_CODE,'client_id': YANDEX_ID,'client_secret': YANDEX_PASS}
	r = requests.post("https://oauth.yandex.ru/token", data= query, headers=YANDEX_REQUEST)

	if(r.status_code==200):
		data = r.json()
		access_token = data['access_token']
		mycache['access_token'] = access_token
		mycache.sync()
	else:
		print('todo: sentry here')
		exit()

else:
	access_token = mycache["access_token"]
	print(access_token)


query = {'oauth_token': access_token}
r = requests.get("https://api-metrica.yandex.com/management/v1/counters", params = query,  headers=YANDEX_REQUEST)

if r.status_code==200:
	content = r.text.encode("UTF-8").decode("UTF-8").strip()
	j = json.loads(content)
	for index in range(len(j['counters'])):

		cid = j['counters'][index]['id']

		print(cid)
		print(j['counters'][index]['name'])

		d = datetime.datetime.now()
		last_date = ''.join(str(x) for x in (d.year, d.month, d.day))

		first_date = (datetime.date.today() - datetime.timedelta(days=360)).isoformat().replace('-','')
		last_date = datetime.date.today().isoformat().replace('-','')

		if ALL:
			query = {
				'oauth_token': access_token,
				'id':cid,
				'date1':first_date,
				'metrics':'ym:pv:pageviews',
				'dimensions':'ym:pv:URLPathFull,ym:pv:title',
				'sort':'-ym:pv:pageviews',
				'date2':last_date
				}
		else:
			query = {
				'oauth_token': access_token,
				'id':cid,
				'date1':first_date,
				'metrics':'ym:pv:pageviews',
				'dimensions':'ym:pv:URLPathFull,ym:pv:title',
				'sort':'-ym:pv:pageviews',
				'filters' :'ym:pv:URL=~\'/'+MY_SLUG+'\'',
				'date2':last_date
				}

		sr = requests.get('https://api-metrica.yandex.com/stat/v1/data', params = query,  headers=YANDEX_REQUEST)
		content = sr.text.encode("UTF-8").decode("UTF-8").strip()

		print(sr.json())

		index+= 1

else:
	print('todo: sentry here')
	exit()



exit()
mycache.close()
