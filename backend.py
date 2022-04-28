import os
import subprocess
import time

from pymongo import MongoClient
from queue import Queue
from subprocess import PIPE, run
from datetime import datetime
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET

client = MongoClient(host="localhost", port=27017)
hintsDB = client["bakatoo"]["hints"]
resultsDB = client["bakatoo"]["results"]

# print(client)
# print(hintsDB)
# print(resultsDB)

pkgs = ["com.example.app1", "com.example.app2"]
accepted = ["homework1", "homework2"]
def validate(request):
    homework = request.form["homework"]
    if homework not in accepted:
        print("Ei läbinud validatsiooni")
        return False, "Seda kodutööd hetkel (või enam) esitada ei saa."

    fCopy = request.files['file']
    fCopy.save(os.path.join("uploads/", secure_filename('valideeritav-app.apk')))
    fCopy.seek(0)
    p_name = cmd(r'aapt dump badging D:\TU\Bakatoo\flaskProject\uploads\valideeritav-app.apk | findstr package',
                       r'C:\Users\sanma\AppData\Local\Android\Sdk\build-tools\32.0.0').split(' ')[1].split('\'')[1]
    #print(p_name)
    if p_name not in pkgs:
        print("Ei läbinud validatsiooni")
        return False, "Ebakorrektne package name, kontrolli üle oma rakenduse applicationId mooduli build.gradle-st."

    queueSize = queue.qsize() + 1 if working else queue.qsize()
    if queueSize >= 10:
        print("Järjekord on täis")
        return False, "Järjekord on hetkel täis, proovige esitada mõne minuti pärast uuesti."
    print("Fail valideeriti.")
    return True, ""


working = False
queue = Queue()
def handle_post():
    global working, queue
    if working:
        time.sleep(1)
        return handle_post()
    if not working:
        working = True
        request, saabunud = queue.get()
        fail = request.files['file']
        matrikkel = request.form['matrikkel']
        #print(fail.filename, matrikkel)
        fail.save(os.path.join("uploads/", secure_filename('testitav-app.apk')))  # fail.filename
        print('Fail kätte saadud, algab testimine.')
        algus = datetime.now()
        exec_bats()

        results, percent = get_results(matrikkel, saabunud, algus)
        working = False
        return results, percent


package_name = ""
def exec_bats():
    global package_name
    # Testimine adb-ga
    print("Rootin telefoni")
    subprocess.call([r'D:\TU\Bakatoo\flaskProject\bats\rootPhone.bat'])
    print("Installin rakendust")
    subprocess.call([r'D:\TU\Bakatoo\flaskProject\bats\installApps.bat'])
    print("Viin läbi teste")
    subprocess.call([r'D:\TU\Bakatoo\flaskProject\bats\execTests.bat'])
    print("Laen alla testide tulemusi")
    subprocess.call([r'D:\TU\Bakatoo\flaskProject\bats\pullReport.bat'])

    package_name = cmd(r'aapt dump badging D:\TU\Bakatoo\flaskProject\uploads\testitav-app.apk | findstr package',
                       r'C:\Users\sanma\AppData\Local\Android\Sdk\build-tools\32.0.0').split(' ')[1].split('\'')[1]

    print("Uninstallin rakendust")
    subprocess.call([r'D:\TU\Bakatoo\flaskProject\bats\uninstallApp.bat'])
    return


def cmd(command, cwd=os.getcwd()):
    process = run(command, cwd=cwd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return process.stdout


#print(cmd("whoami"))
#print(cmd(r'aapt dump badging D:\TU\Bakatoo\flaskProject\uploads\testitav-app.apk | findstr package',
#                       r'C:\Users\sanma\AppData\Local\Android\Sdk\build-tools\32.0.0'))

def get_results(matrikkel, arrivalTime, startTime):
    global package_name

    tree = ET.parse('pulled/files/report-0.xml')
    root = tree.getroot()
    results = []
    for elem in root.iter():
        if elem.tag == 'testcase':
            test = list(elem.attrib.values())[0].replace('.', '(').split('(')
            nimi = test[0]
            tyyp = test[-1][:-1]
            aeg = list(elem.attrib.values())[-1]
            tulemus = "Success"
            errorMes = "Success"
            vihje = get_hint(nimi, tyyp)
            # print(vihje)
            results.append([nimi, tyyp, aeg, tulemus, errorMes, vihje])
        elif elem.tag == 'failure':  # kui test ei läinud läbi
            # print(list(elem.attrib.values())[1])
            results[-1][3] = "Failure"
            results[-1][4] = list(elem.attrib.values())[1]

    resList = [result[3] for result in results]
    percent = (resList.count("Success") / len(results)) * 100
    log_result(matrikkel, package_name, percent, arrivalTime, startTime)

    return results, percent


def get_hint(nimi, tyyp):
    global hintsDB
    hint = ""
    testClass = hintsDB.find({"classname": tyyp})
    for test in testClass[0]["tests"]:
        if test["name"] == nimi:
            hint = test["hint"]
            break
    return hint


def log_result(matrikkel, pack_name, percent, saabunud, algus):
    global resultsDB
    saabunud = saabunud.strftime("%d.%m.%Y %H:%M:%S")
    algus = algus.strftime("%d.%m.%Y %H:%M:%S")
    lopp = datetime.now()
    lopp = lopp.strftime("%d.%m.%Y %H:%M:%S")
    log = {
        "SIS_ID": matrikkel, "Homework": pack_name, "Result": percent,
        "ArrivalTime": saabunud, "TestingStart": algus, "TestingEnd": lopp
    }
    resultsDB.insert_one(log)
    return

# exec_bats()
