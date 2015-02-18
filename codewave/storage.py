import os.path
import json
import sublime
 
CONFIG_FILE = os.path.join(sublime.packages_path(), 'Codewave', 'config.json')

def save(key,val):
	f = None
	try:
		if os.path.isfile(CONFIG_FILE) : 
			f = open(CONFIG_FILE, 'r+')
			data = _getData(f)
			f.seek(0)
			if data is None :
				data = {}
		else :
			if not os.path.exists(os.path.dirname(CONFIG_FILE)):
				os.makedirs(os.path.dirname(CONFIG_FILE))
			f = open(CONFIG_FILE, 'w')
			data = {}
		data[key] = val
		f.write(json.dumps(data, indent=2, separators=(',', ': ')))
		f.truncate()
	finally:
		if f is not None :
			f.close()
	
def load(key):
	if os.path.isfile(CONFIG_FILE) : 
		f = open(CONFIG_FILE, 'r')
		try:
			data = _getData(f)
		finally:
			f.close()
		if data is not None and key in data :
			return data[key]
			
def _getData(f):
	raw = f.read()
	if len(raw) :
	  return json.loads(raw)