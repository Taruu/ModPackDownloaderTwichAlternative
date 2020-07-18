import  requests
import json
import zipfile
import os
import shutil
import cfscrape
from bs4 import BeautifulSoup
import hashlib

#TODO logger

servers = "https://raw.githubusercontent.com/Taruu/TANDOTS/master/server.json"

class GetConfig:
    def __init__(self,Settings):
        self.Settings = Settings
        self.scraper = cfscrape.create_scraper()
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
        with open(path_work_folder+"/modlistdownload.json") as modlist_file:
            newModList = json.load(modlist_file)
        print(len(newModList))
        return newModList

    def DownloadMods(self,progressBar,path_work_folder,dataMod):
        print("pathh",path_work_folder)
        path_for_mods = path_work_folder + f"/mods/{dataMod['filename']}"
        link = dataMod["link"]
        hash_mod = dataMod["md5hash"]
        mod = self.scraper.get(link, stream=True)
        content_length = mod.headers.get("Content-Length")
        if link.startswith('https://www.curseforge.com'):
            mod_screen = self.scraper.get(link)
            soup = BeautifulSoup(mod_screen.text)
            haslink = soup.findAll("p", {"class": "text-sm"})[0]
            url = "https://www.curseforge.com" + haslink.findAll("a", href=True)[0].get('href')
            mod_download = self.scraper.get(url, stream=True)
            content_length = mod_download.headers.get("Content-Length")
            while not (content_length):
                mod_download = self.scraper.get(url, stream=True)
                content_length = mod.headers.get("Content-Length")
        else:
            mod_download = requests.get(link,stream=True)
            content_length = mod.headers.get("Content-Length")
            while not (content_length):
                mod_download = requests.get(link,stream=True)
                content_length = mod.headers.get("Content-Length")


        with open(path_for_mods, 'wb') as ModFile:
            progressBar.setMaximum(int(content_length) // 1024)
            for i, chunk in enumerate(mod_download.iter_content(chunk_size=1024)):
                progressBar.setValue(i)
                ModFile.write(chunk)
                ModFile.flush()
            ModFile.close()
        with open(path_for_mods,"rb") as ModFile:
            HashBytes = ModFile.read()
            readable_hash = hashlib.md5(HashBytes).hexdigest()
        if readable_hash != hash_mod:
            os.remove(path_for_mods)
        return True


