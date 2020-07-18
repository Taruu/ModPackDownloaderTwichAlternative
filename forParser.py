import json
from bs4 import BeautifulSoup
import cloudscraper
with open("old.json") as file:
    json_data = json.load(file)
result_json = []
print(json_data)
scraper = cloudscraper.create_scraper()
for mod in json_data:
    if mod["link"].startswith("https://www.curseforge.com"):
        list_link = mod["link"].split("download")
        fileId = int(str(list_link[-1])[1:])
        filename = list_link[0].split("/")[-2] +".jar"


        soup = BeautifulSoup(scraper.get(list_link[0]).text)
        dagta = soup.find("div", {"class": "w-full flex justify-between"})
        res = dagta.findAll("span")[-1]
        project_id = str(res)[6:-7]
        print(project_id,fileId,filename)
        result_json.append({"projectId":int(project_id),"fileId":fileId,"filename":filename,"optional":mod["optional"]})
    else:
        result_json.append(
            {"projectId": None, "fileId": None, "filename": mod["filename"], "optional": mod["optional"],"url":mod["link"],"md5hash":mod["md5hash"]})

print(json.dumps(result_json))
