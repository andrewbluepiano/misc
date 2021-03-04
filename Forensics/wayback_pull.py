# A program for grabbing URL's of specific MIME types from the wayback archive. 
# Uses WaybackClient now, will move to just the CDX url filter soon.
# Author: Andrew Afonso
from wayback import WaybackClient
import csv
import os
import sys
import datetime
import json

# Results data holder class
class wbResult:
	def __init__(self, results):
		self.results = results
		self.mimetypes = []
		self.toGrab = []
		self.toSkip = []

# Help messages
def help():
	print("-----------")
	print("Basic Usage")
	print("-----------")
	print("python wayback_pull.py <website.url.com> [options]")
	print("Outputs a CSV file with results of selected MIME types")
	print("\n-----------")
	print("Options")
	print("-----------")
	print("\t-L <filename.json>")
	print("\t\tLoad an existing log file to filter using previous results. Additional choices will be provided.")

	sys.exit()

# Error messages
def error(n):
	if n == 1:
		sys.exit("Not enough arguments (use -h for help).\n")
	if n == 2:
		sys.exit("Invalid config filename specified (use -h for help).\n")


# CSV Row Writer
def writeRecord(csvwriter, record):
	csvwriter.writerow([ record.url, record.mime_type, record.status_code, record.timestamp, record.digest, record.length, record.raw_url, record.view_url])

# Log Writer
def writeCaptureLog(wbResults, dtNowStr, bigDataFileName):
	logOutFileName = 'log_' + dtNowStr + '.json'
	with open(logOutFileName, 'w') as logOutFile:
		json.dump({ "Output_Data_File" : bigDataFileName, "MIME_Types_Collected" : wbResults.toGrab, "MIME_Types_Skipped" : wbResults.toSkip }, logOutFile)
	logOutFile.close()
	
	
# Main
def main():
	if len(sys.argv) < 2:
		help()

	if "-L" in sys.argv:
		if len(sys.argv) < 4:
			error(1)
		if ".json" not in sys.argv[sys.argv.index("-L") + 1]:
			error(2)
		else:
			print("\nIt looks like you loaded an existing project config. Pick how you want to use this:")
			print("[1] - Collect and ignore the same MIME Type URL's as specified in the previous session.")
			print("[2] - Ignore the MIME Types collected in the previous session")
			loadMethod = input("Enter load method: ")

	wbClient = WaybackClient()
	results = wbClient.search( sys.argv[1], matchType="domain", collapse="digest", resolveRevisits=True, skip_malformed_results=False)
	wbResults = wbResult(results)
	
	if "-L" in sys.argv:
		configFile = open(sys.argv[sys.argv.index("-L") + 1], 'r')
		configsTemp = json.load(configFile)
		if int(loadMethod) == 1:
			wbResults.mimetypes = configsTemp["MIME_Types_Collected"] + configsTemp["MIME_Types_Skipped"]
			wbResults.toGrab = configsTemp["MIME_Types_Collected"]
			wbResults.toSkip = configsTemp["MIME_Types_Skipped"]
		if int(loadMethod) == 2:
			wbResults.mimetypes = configsTemp["MIME_Types_Collected"]
			wbResults.toSkip = configsTemp["MIME_Types_Collected"]
			
	
	
	dtNowStr = (datetime.datetime.now()).strftime("%m-%d-%Y %H-%M-%S")
	bigDataFileName = 'wayback_out ' + dtNowStr + '.csv'
	
	with open(bigDataFileName, 'w', newline='') as outputFile:
		csvwriter = csv.writer(outputFile)
		csvwriter.writerow([ "URL", "mime_type", "Status_Code", "Timestamp", "Digest", "Length", "Raw_URL", "View_URL"])
		while 1==1:
			try:
				record = next(results)
				if record.mime_type in wbResults.mimetypes:
					if record.mime_type in wbResults.toGrab:
						writeRecord(csvwriter, record)
				if record.mime_type not in wbResults.mimetypes:
					print("New Mime Type discovered: " + record.mime_type)
					wbResults.mimetypes.append(record.mime_type)
					choice = input("Enter 1 to grab URLs with this MIME Type, 0 to skip: ") 
					if int(choice) ==  1:
						wbResults.toGrab.append(record.mime_type)
						writeRecord(csvwriter, record)
					if int(choice) == 0:
						wbResults.toSkip.append(record.mime_type)
			except:
				break
	
	outputFile.close()	
	writeCaptureLog(wbResults, dtNowStr, bigDataFileName)

 
if __name__ == "__main__":
	main()