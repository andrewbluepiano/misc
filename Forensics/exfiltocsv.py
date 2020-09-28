# Filename: 	exiftocsv.py
# Author: 		Andrew Afonso
# Description:	Reads in a plaintext file that contains the output of Phil Harvey's ExifTool file, and outputs
#				a csv file containing the data.
import csv
import os
import sys

def main():
	inputFilePath = sys.argv[1]
	inputFile = open(inputFilePath, 'r')
	inputContents = inputFile.readlines()
	mdTags = set()
	mdTags.add("Filename")
	
	with open('exifout.csv', 'w', newline='') as outFile:
		csvwriter = csv.writer(outFile)
		csvwriter.writerow(["MDTag", "Value"])
		for line in inputContents:
			# Prevent the last line which totals the files read from being processed.
			if line[0:2] != "  ":
				line = line.strip()
				# If line is filename
				if line[0:7] == "=======":
					# Snip out filename, write to CSV
					csvwriter.writerow(["Filename", line[9:]])
				# Else line is metadata tag:val pair
				else:
					lineData = line.split(":")
					mdKey = lineData[0].strip()
					mdTags.add(mdKey)
					mdVal = lineData[1].strip()
					csvwriter.writerow([mdKey, mdVal])
					
	
	with open('mdTags.csv', 'w', newline='') as mdTagFile:
		tagcsvwriter = csv.writer(mdTagFile)
		mdTags = sorted(mdTags)
		for mdTag in mdTags:
			tagcsvwriter.writerow([mdTag])

if __name__ == "__main__":
    main()
