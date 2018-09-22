# Given a folder, scan all files and group file with same content

import sys
import os
import shutil
import hashlib
import time
from collections import defaultdict
import multiprocessing 
from functools import partial
import time

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

def Process(filename, dirpath, dic, autoDelete):
    start = time.time()
    filename = os.path.join(dirpath, filename)
    signature = ExtractFingerprint(filename, 512)
    if signature:
        dic[signature].append(filename)
        if len(dic[signature]) > 1:
            CreateDir(os.path.join("output", signature))
            with open(os.path.join("output", signature ,signature +".txt"), "a+") as f:
                print("\n",signature)
                print("\n".join(dic[signature]))

                if autoDelete:
                    CreateDir(os.path.join("deleted",signature))
                    moveDeletedFileTo = os.path.join("deleted",signature)

                if len(dic[signature]) == 2:
                    if autoDelete:
                        shutil.move(filename,moveDeletedFileTo)
                        f.write(dic[signature][0] + "\n")
                        f.write("[DELETED] " + dic[signature][1] + "\n")
                    else:
                        shutil.copy(filename,os.path.join("output", signature))
                        shutil.copy(dic[signature][0],os.path.join("output", signature))
                        f.write("\n".join(dic[signature]) + "\n")
                else:
                    if autoDelete:
                        shutil.move(filename,moveDeletedFileTo)
                        f.write("[DELETED] " + filename + "\n")
                    else:
                        shutil.copy(filename,os.path.join("output", signature))
                        f.write(filename + "\n")
                f.close()
        return (time.time() - start) * 1000

if __name__ == '__main__':
    dics = defaultdict(list)
    multiprocessing.managers.DictProxy
    folderPath = sys.argv[sys.argv.index("-p")+1] if "-p" in sys.argv else ""
    isAutoDelete = "-d" in sys.argv
    signature_size = 512
    if "-b" in sys.argv:
        signature_size = int(sys.argv[sys.argv.index("-b")+1])

    cpuCount = multiprocessing.cpu_count()
    print("Using Signature Size of ", signature_size)
    print("Using CPU Cores of ", cpuCount)

    if len(sys.argv) == 1 or not os.path.isdir(folderPath):
        print("Run with python \"dedup.py [parameters]\"")
        print("[Param] -p = \"Path to scan for duplicates\"")
        print("[Optional Param] -d = \"Delete Duplicate\"")
        print("[Optional Param] -b number = \"Change the default signature size of 512 bits\"")
        exit(0)   

    CreateDir("output")
    if isAutoDelete:
        CreateDir("deleted")

    processedCount = 0
    average = 0
    with multiprocessing.Pool(processes=cpuCount) as pool:
        for (dirpath, dirnames, filenames) in os.walk(folderPath):
            if len(filenames) > 0:
                sys.stdout.write("Scanning: %d Total: %d Dic-Size: %d Avg-Duration: %d \r" % (len(filenames), processedCount, len(dics), average))
                process_local = partial(Process, dirpath=dirpath, dic=dics, autoDelete=isAutoDelete)
                result = pool.map(process_local, filenames)
                totalResult = len(result)
                processedCount += totalResult
                average = sum(result) / totalResult
