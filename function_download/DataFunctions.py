import  requests
import json
import zipfile
import os
import shutil
from bs4 import BeautifulSoup
import hashlib

#TODO logger

servers = "https://raw.githubusercontent.com/Taruu/TANDOTS/master/server.json"

class GetConfig:
    def __init__(self,Settings):
        self.Settings = Settings
        self.requestsSession = requests.Session()
        self.requestsSession.headers.update({'User-Agent': 'Tandots updateer','From': 'tandots.ru'})
        temp_result = requests.get(servers)
        if temp_result.status_code == 200:
            serverList = temp_result.json()

        listConf = self.Settings.allKeys()
        for serverLocal in listConf:
            if not(serverLocal in serverList):
                self.Settings.remove(serverLocal)
        for serverWeb in serverList:
            if not(serverWeb in listConf):
                self.Settings.setValue(serverWeb,{"name":serverWeb,"git":serverList[serverWeb],"path":None,"modList":None})
            else:
                if serverList[serverWeb] != self.Settings.value(serverWeb)["git"]:
                    tempServerSettings = self.Settings.value(serverWeb)
                    tempServerSettings["git"] = serverList[serverWeb]
                    self.Settings.setValue(serverWeb,tempServerSettings)


    def CloneGit(self,url, path_zip, progressBar): #TODO progressBar add and etc...
        allZip = requests.get(url,stream=True)
        content_length = allZip.headers.get("Content-Length")
        while not(content_length):
            allZip = requests.get(url, stream=True)
            content_length = allZip.headers.get("Content-Length")
        with open(path_zip, 'wb') as ZipClone:
            progressBar.setMaximum(int(content_length)//1024)
            for i,chunk in enumerate(allZip.iter_content(chunk_size=1024)):
                progressBar.setValue(i)
                ZipClone.write(chunk)
                ZipClone.flush()
            ZipClone.close()

        work_path = os.path.dirname(path_zip)

        with zipfile.ZipFile(path_zip, 'r') as zip_ref:
            path_extacted = zip_ref.namelist()[0]
            zip_ref.extractall(path=work_path)

        for absolute, _,items in os.walk(work_path+"/"+path_extacted):
            absolute_path_need = absolute.replace("TBN3-master/", "")

            for file in items:
                if not(os.path.exists(absolute_path_need)):
                    os.mkdir(absolute_path_need)
                print(os.path.isdir(absolute_path_need),absolute_path_need)
                if os.path.isdir(absolute_path_need):
                    shutil.move(absolute +"/"+ file, absolute_path_need +"/"+ file)
                else:
                    shutil.move(absolute + file, absolute_path_need + file)
        shutil.rmtree(work_path+"/"+path_extacted,)
        os.remove(path_zip)


    def ListMods(self,path_work_folder):
        print(path_work_folder)
        with open(path_work_folder+"/listmod.json") as modlist_file: #тут список модов меняем если че
            newModList = json.load(modlist_file)
        print(len(newModList))
        return newModList

    def GetUrlMod(self,projectId,fileId):
        response = self.requestsSession.get(f"https://addons-ecs.forgesvc.net/api/v2/addon/{projectId}/file/{fileId}/download-url")
        return response.text

    def DownloadMods(self,progressBar,path_work_folder,dataMod):
        print("pathh",path_work_folder)
        path_for_mods = path_work_folder + f"/mods/{dataMod['filename']}"
        if dataMod.get('projectId'):
            linkToMod = self.GetUrlMod(dataMod["projectId"],dataMod["fileId"])
        else:
            linkToMod = dataMod["url"]

        modStream = self.requestsSession.get(linkToMod, stream=True)
        content_length = modStream.headers.get("Content-Length")
        while not (content_length):
            modStream = self.requestsSession.get(linkToMod, stream=True)
            content_length = modStream.headers.get("Content-Length")

        with open(path_for_mods, 'wb') as ModFile:
            progressBar.setMaximum(int(content_length) // 1024)
            for i, chunk in enumerate(modStream.iter_content(chunk_size=1024)):
                progressBar.setValue(i)
                ModFile.write(chunk)
                ModFile.flush()
            ModFile.close()
        return True


