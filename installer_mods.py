import sys
import os
from pathlib import Path
from PyQt5 import QtGui
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings, QThread
from PyQt5.QtWidgets import QMessageBox
from function_download import DataFunctions

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('design/main.ui', self)
        met = QtGui.QFontMetrics(QtGui.QFont())


        self.settings = QSettings('dataConfig', 'Tandots')
        print()

        #custom function import here
        self.GetConfig = DataFunctions.GetConfig(self.settings)
        #self.settings.clear()




        #Take all elements
        self.comboBoxServer = self.findChild(QtWidgets.QComboBox,"comboBoxServer") #box on now server
        self.pathMinecraft = self.findChild(QtWidgets.QLineEdit,"pathMinecraft") #path to mods
        self.pushButtonTakePath = self.findChild(QtWidgets.QPushButton,"pushButtonTakePath") #take path button
        self.pushButtonDownload = self.findChild(QtWidgets.QPushButton,"pushButtonDownload") #download button

        self.progressBar = self.findChild(QtWidgets.QProgressBar,"progressBar") #download_mod progressBar

        self.labelCountMods = self.findChild(QtWidgets.QLabel,"labelCountMods") #status / mods count label
        self.labelPathInfo = self.findChild(QtWidgets.QLabel,"labelPathInfo") #status path

        self.comboBoxServer.currentTextChanged.connect(self.takeServer)
        self.pathMinecraft.editingFinished.connect(self.saveNowPath)
        self.pushButtonTakePath.pressed.connect(self.takePath)
        self.pushButtonDownload.pressed.connect(self.downloadAll)

        for item in self.settings.allKeys():
            self.comboBoxServer.addItem(item.upper())

        #init event functionality

        self.nowServer = self.settings.value(self.comboBoxServer.currentText().lower())
        self.check_path()
        self.path = None
        self.show()


    def check_path(self):
        path = self.pathMinecraft.text()
        if os.path.exists(path) and "minecraft" in path:
            if os.path.exists(path+"/mods"):
                self.saveNowPath()
                self.path = path
                self.labelPathInfo.setText("Path is OK!")
            else:
                self.labelPathInfo.setText("Not path mods!")
                self.path = None
                buttonReply = QMessageBox.question(self, 'Не нашли папку Mods...', "Не найдена папка mods, создать? По адресу:\n{}".format(path), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.labelPathInfo.setText("Path is OK!")
                    self.saveNowPath()
                    self.path = path
                    os.mkdir(path+"/mods")
                else:
                    self.labelPathInfo.setText("Not path mods!")
                    self.path = None
        else:
            self.labelPathInfo.setText("Not correct path!")
            self.path = None



    def takeServer(self, text):
        self.nowServer = self.settings.value(text.lower())
        if self.nowServer["path"]:
            self.pathMinecraft.setText(self.nowServer["path"])
        else:
            self.pathMinecraft.clear()

    def saveNowPath(self):
        print(self.nowServer,self.pathMinecraft.text())
        self.nowServer["path"] = self.pathMinecraft.text()
        self.settings.setValue(self.nowServer["name"],self.nowServer)

    def takePath(self):
        if os.path.exists(self.pathMinecraft.text()):
            temp_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open mods directory',self.pathMinecraft.text())
            print("path", temp_dir)
            if len(temp_dir) > 2:
                self.pathMinecraft.setText(temp_dir)
            else:
                pass
        else:
            temp_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open mods directory', str(Path.home()))
            print("path",temp_dir)
            if len(temp_dir)>2:
                self.pathMinecraft.setText(temp_dir)
            else:
                pass


        self.nowServer["path"] = self.pathMinecraft.text()
        self.settings.setValue(self.nowServer["name"], self.nowServer)
        self.check_path()

    def findByName(self,name, ListMods): #Костыль лять
        for mod in ListMods:
            if mod["filename"] == name:
                return mod
        else:
            return None

    def downloadAll(self):
        listModsToDownload = []
        path = self.nowServer["path"]
        self.labelCountMods.setText("Скачивание конфигов")
        print(self.nowServer["git"],path)
        self.GetConfig.CloneGit(self.nowServer["git"],path+"/ZipClone.zip",self.progressBar)
        self.labelCountMods.setText("Скачивание модов")
        if self.nowServer["modList"]:
            OldServerMods = self.nowServer["modList"]
        else:
            OldServerMods = None
        NewServerMods = self.GetConfig.ListMods(path)

        if not(OldServerMods):
            self.nowServer["modList"] = NewServerMods
            self.DownloadWorkerMain(path, listModsToDownload)
            self.settings.setValue(self.nowServer["name"], self.nowServer)
            return

        for NewMod in NewServerMods:
            oldMod = self.findByName(NewMod["filename"],OldServerMods)
            if oldMod:
                if oldMod["md5hash"] != NewMod["md5hash"]:
                    os.remove(path + "/mods/" + oldMod["filename"])
                    listModsToDownload.append(NewMod)
        for OldMod in OldServerMods:
            NewMod = self.findByName(OldMod["filename"],NewServerMods)
            if not(NewMod):
                try:
                    os.remove(path + "/mods/" + oldMod["filename"])
                except:
                    pass
                continue
            modfile = Path(path + "/mods/" + NewMod["filename"])
            if not(modfile.exists()):
                listModsToDownload.append(NewMod)
        self.DownloadWorkerMain(path,listModsToDownload)
        self.nowServer["modList"] = NewServerMods
        self.settings.setValue(self.nowServer["name"], self.nowServer)





    def DownloadWorkerMain(self,path,listMods):
        self.labelCountMods.setText(f"Скачиваем моды: 0/{len(listMods)}")
        for i, mod in enumerate(listMods):
            print("downloadWorker", mod)
            self.labelCountMods.setText(f"Скачиваем моды: {i+1}/{len(listMods)}")
            self.GetConfig.DownloadMods(self.progressBar, path, mod)
        else:
            # QMessageBox.question(self, "Статус", "Все установленно!", QMessageBox.Ok)
            self.labelCountMods.setText("Устоновка завершена!")




class DownloadWorker(QThread):
    def __init__(self, labelCountMods, ProgressBar, GetConfig,path, listMods, parent=None):
        super().__init__()
        self.labelCountMods = labelCountMods
        self.GetConfig = GetConfig
        self.ProgressBar = ProgressBar
        self.path = path
        self.listMods = listMods
    def run(self):
        pass


    def stop(self):
        self.terminate()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
