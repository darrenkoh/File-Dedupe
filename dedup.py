# Given a folder, scan all files and group file with same content

import sys
import os
import shutil
import hashlib
import time
from collections import defaultdict
from joblib import Parallel, delayed
import multiprocessing

def ExtractFingerprint(filename, bit):
    size = os.path.getsize(filename)
    sign = None
    signature = hashlib.sha1()
    signatureStep = size // bit
    
    with open(filename, "rb") as f:
        if signatureStep > 0:
            stepIndex = signatureStep
            while stepIndex < size:
                f.seek(stepIndex)
                signature.update(f.read(1))
                stepIndex += signatureStep
        elif size > 0:
            signature.update(f.read())
        f.close()
    
    if size > 0:
        sign = signature.hexdigest()
    return sign

def CreateDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

folderPath = sys.argv[sys.argv.index("-p")+1] if "-p" in sys.argv else ""
autoDelete = "-d" in sys.argv
signature_size = 512
if "-b" in sys.argv:
    signature_size = int(sys.argv[sys.argv.index("-b")+1])

print("Using Signature Size of ", signature_size)
print("Using MultiCores of ", multiprocessing.cpu_count())

if len(sys.argv) == 1 or not os.path.isdir(folderPath):
    print("Run with python \"dedup.py [parameters]\"")
    print("[Param] -p = \"Path to scan for duplicates\"")
    print("[Optional Param] -d = \"Delete Duplicate\"")
    print("[Optional Param] -b number = \"Change the default signature size of 512 bits\"")
    exit(0)

dic = defaultdict(list)

CreateDir("output")
if autoDelete:
    CreateDir("deleted")

for (dirpath, dirnames, filenames) in os.walk(folderPath):
    processedCount = 0
    print("Scanning ", dirpath)
    for filename in filenames:
        processedCount += 1
        sys.stdout.write("Scanning: %d/%d Dic-Size: %d\r" % (processedCount, len(filenames), len(dic)) )
        filePath = os.path.join(dirpath,filename)
        signature = ExtractFingerprint(filePath, 512)
        if signature:
            dic[signature].append(filePath)
            if len(dic[signature]) > 1:
                CreateDir(os.path.join("output", signature))
                with open(os.path.join("output", signature ,signature +".txt"), "a+") as f:
                    print("\n",signature)
                    print("\n".join(dic[signature]))

                    if autoDelete:
                        CreateDir(os.path.join("deleted",signature))
                        moveDeletedFileTo = os.path.join("deleted",signature, filename)

                    if len(dic[signature]) == 2:
                        if autoDelete:
                            shutil.move(filePath,moveDeletedFileTo)
                            f.write(dic[signature][0] + "\n")
                            f.write("[DELETED] " + dic[signature][1] + "\n")
                        else:
                            shutil.copy(filePath,os.path.join("output", signature, filename))
                            shutil.copy(dic[signature][0],os.path.join("output", signature))
                            f.write("\n".join(dic[signature]) + "\n")
                    else:
                        if autoDelete:
                            shutil.move(filePath,moveDeletedFileTo)
                            f.write("[DELETED] " + filePath + "\n")
                        else:
                            shutil.copy(filePath,os.path.join("output", signature, filename))
                            f.write(filePath + "\n")
                    f.close()