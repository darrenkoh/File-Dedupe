# Given a folder, scan all files and group file with same content

import sys
import os
import shutil
import hashlib
import time
from collections import defaultdict

def ExtractFingerprint(filename, bit):
    size = os.path.getsize(filename)
    sign = None
    signature = hashlib.sha1()
    signatureSize = size // bit
    
    with open(filename, "rb") as f:
        if signatureSize > 0:
            stepIndex = 0
            signatureIndex = 0
            while stepIndex < size and signatureIndex < signatureSize:
                f.seek(stepIndex)
                signature.update(f.read(1))
                signatureIndex += 1
                stepIndex += bit
        elif size > 0:
            signature.update(f.read())
        f.close()
    
    if size > 0:
        sign = signature.hexdigest()
    
    return sign

folderPath = None
autoDelete = "-d" in sys.argv
if not folderPath:
    if len(sys.argv) == 1 or not os.path.isdir(sys.argv[1]):
        print("Run with python dedup.py path")
        print("[Optional Param] -d \"Delete Duplicate\"")
        exit(0)

folderPath = sys.argv[1]

dic = defaultdict(list)

if not os.path.isdir("output"):
    os.makedirs("output")

if autoDelete and not os.path.isdir("deleted"):
    os.makedirs("deleted")

for (dirpath, dirnames, filenames) in os.walk(folderPath):
    for filename in filenames:
        filePath = dirpath + "/" + filename
        signature = ExtractFingerprint(filePath, 512)
        if signature:
            dic[signature].append(filePath)
            if len(dic[signature]) > 1:
                with open("output/" + signature, "a+") as f:
                    print("\n",signature)
                    print("\n".join(dic[signature]))

                    if autoDelete:
                        if not os.path.isdir("deleted/" + signature):
                            os.makedirs("deleted/" + signature)
                        moveDeletedFileTo = "deleted/" + signature + "/" + filename

                    if len(dic[signature]) == 2:
                        if autoDelete:
                            shutil.move(filePath,moveDeletedFileTo)
                            f.write(dic[signature][0] + "\n")
                            f.write("[DELETED] " + dic[signature][1] + "\n")
                        else:
                            f.write("\n".join(dic[signature]) + "\n")
                    else:
                        if autoDelete:
                            shutil.move(filePath,moveDeletedFileTo)
                            f.write("[DELETED] " + filePath + "\n")
                        else:
                            f.write(filePath + "\n")
                    f.close()