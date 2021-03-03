# Author: Andrew Afonso
# A program for removing timestamps and empty lines from transcript files (vtt)
import sys
import os

def main():
    filepath = ""
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
    else:
        print("Please enter the transcript file you want to clean as a program argurment.")
        print("Ex: python ccfixer.py \"transcript 445 words.txt\"")
        exit()
    fout = open("Cleaned "+filepath, "w")

#    if not os.path.exists("output"):
#        os.mkdir("output")

    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            #print("Line {}: {}".format(cnt, line.strip()))
            line = fp.readline()
            try:
                if line[0] != "" and line[0] != "\n" and line[0] != "0" :
                    fout.write(line)
            except IndexError as indexerror:
                continue
            cnt += 1
    fout.close()
    
if __name__ == "__main__":
    main()
