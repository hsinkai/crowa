#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# wget -S --no-check-certificate --no-proxy -O O-A0018-001.xml "https://opendata.cwb.gov.tw/opendataapi?dataid=O-A0018-001&Authorization=$apikey&format=XML"
#

import sys
import getopt
import urllib2

APIkey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
cachePath = "/tmp/etagcache/"

_HELP_TEXT = """
	importOpendata.py --dataid=[OPENDATA_DATA_ID] (--target=[OUTPUT_TARGET_PATH] --format=[FORMAT, default xml])

	ex. importOpendata.py --dataid=O-A0018-001
	ex. importOpendata.py --dataid=F-C0032-001 --target=/CRSdata/dataIn/OPENDATA
	ex. importOpendata.py --dataid=W-C0033-003 --format=cap
"""

class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    
	def http_error_default(self, req, fp, code, msg, headers):
		result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)       
		result.status = code
		return result                 

def _parsing_command_argument(argv):
	"""commandline arguments 
	"""
	dataid = ""
	target = ""
	fileFormat = "xml"
	try:
		opts, args = getopt.getopt(argv, "h", 
			("help", "dataid=", "target=", "format="))
		for opt, arg in opts:
			if opt in ('--help','-h'):
				print _HELP_TEXT
				sys.exit(1)
			elif '--dataid' == opt:
				dataid = arg
			elif '--target' == opt:
				target = arg
				if not target.endswith("/"):
					target = target + "/"
			elif '--format' == opt:
				fileFormat = arg
		if dataid == "":
			print _HELP_TEXT
			sys.exit(1)
	except Exception as e:
		sys.stderr.write("Argument Error: %r " % (e,))
		sys.exit(1)
	return (dataid, target, fileFormat)

def getOpenData(dataid, targetPath, outputFormat):
	""" download opendata
	"""
	print "getOpendata", dataid, targetPath, outputFormat
	try:
		etagFile = open(cachePath + dataid)
		lastEtag = etagFile.read()
		etagFile.close()
	except:
		lastEtag = ""
	print "lastEtag", lastEtag	

	reqURL = "http://odapm1.cwb.gov.tw:8080/fileapi/v1/opendataapi/%s?Authorization=%s&format=%s" % (dataid, APIkey, outputFormat)
	print "reqURL", reqURL
	request = urllib2.Request(reqURL)

	if lastEtag != "":
		request.add_header('If-None-Match', lastEtag)

	# Set no proxy
	urllib2.getproxies = lambda: {}
	# 
	opener = urllib2.build_opener(DefaultErrorHandler)

	try:
		firstdatastream = opener.open(request)
		print "Done request", reqURL
	except Exception as e:
		sys.stderr.write("Request Error: %r " % (e,))
		sys.exit(1)

	try:
		dataContent = firstdatastream.read()
		print "Done read data content"
		responseStatus = firstdatastream.getcode()
		print "HTTP response status:",responseStatus
		if len(dataContent) == 0 and responseStatus == 304:
			print "Resource not modified, skip downloading."
			return
 		elif responseStatus >= 400:
			print dataContent
			return
		outputFile = open(targetPath + dataid + "." + outputFormat, "w")
		outputFile.write(dataContent)
		outputFile.close()
		print "Done output file"
	except Exception as e:
		sys.stderr.write("Read datastream or write output file error: %r " % (e,))
		sys.exit(1)
	
	try:
		etag = firstdatastream.headers.get('ETag')
		print "etag:", etag
		etagFile = open(cachePath + dataid, "w")
		print "Update:", cachePath + dataid
		etagFile.write(str(etag))
		etagFile.close()
	except Exception as e:
		sys.stderr.write("Get etag error: %r " % (e,))
		sys.exit(1)
	return

if __name__ == "__main__":
	args = _parsing_command_argument(sys.argv[1:])
	dataid = args[0]
	targetPath = args[1]
	outputFormat = args[2]
	
	getOpenData(dataid, targetPath, outputFormat)

# <<< if __name__ == "__main__":

