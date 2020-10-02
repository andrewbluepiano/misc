#####################################################################
# Filename: Lab5_Script.sh
# Author: Andrew Afonso
#
# Description:
# Performs Metadata export, parsing, and scrubbing using Phil Harvey's ExifTool
#
# Requirements:
# 	Internet connection
# 	curl
# 	exiftocsv.py
# 	python installed and callable using "python"
#####################################################################


#####################################################################
# Setup
#####################################################################
clear
echo "Files should all be in a one level subdirectory of the folder containing this script"
echo "THIS SCRIPT WILL MODIFY AND REMOVE METADATA FROM FILES IN THE SPECIFIED DIRECTORY"
read -p "Enter the directory name containing the files with metadata: " metaDirectory
echo $metaDirectory


#####################################################################
# Get ExifTool
#####################################################################
curl https://exiftool.org/Image-ExifTool-12.07.tar.gz --output Image-ExifTool-12.07.tar.gz
tar -xf Image-ExifTool-12.07.tar.gz


#####################################################################
# Perform Analysis, Save findings to .txt files.
#####################################################################
./Image-ExifTool-12.07/exiftool $metaDirectory/* > ExifOut.txt



#####################################################################
# Parse ExifOut.txt to two seperate CSV files, one with file metadata,
# one with a unique list of MetaData tags
#####################################################################
if ! [ -f exiftocsv.py ]; then
    echo "exiftocsv.py is missing, parsing of ExifTool output impossible"
    exit 1
else
	python exiftocsv.py ExifOut.txt
fi


#####################################################################
# Double check before running destructive functions.
#####################################################################
read -p "Further functions will modify files. Press [Enter] to continue, or [Ctrl] + [c] to exit"


#####################################################################
# Check that files have the appropriate extension. Append correct extension if not.
#####################################################################
for file in $metaDirectory/*
do
	correctExtension=$(./Image-ExifTool-12.07/exiftool -s -s -s -filetypeextension $file)
	correctExtensionLength=$(echo -n $correctExtension | wc -c)
	currentEnding=$(echo -n $file | tail -c $correctExtensionLength)
	if [ "$currentEnding" != "$correctExtension" ]; then
		mv $file "${file}.${correctExtension}"
	fi
done


#####################################################################
# Scrub MetaData
#####################################################################
./Image-ExifTool-12.07/exiftool -all= -overwrite_original allfiles/.
