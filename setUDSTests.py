import os
import sys
import threading
from zipfile import ZipFile
from UnitTestUDS import setTests

class runTests:
    topFolder = 'RegressionTests'
    ap_rules = 'ap_rules.dslr'
    sp_rules = 'sp_rules.dslr'
    mapping = 'column-map1.json'

    unitTests = len(os.listdir(topFolder))

    def checkZip(self, folder):
        return any(file.endswith('.zip') for file in os.listdir(folder))

    def extractZipFile(self, actualFolder, unzippedFolder):
        for zipFile in unzippedFolder:
            try:
                unzippedDir = f"{actualFolder}/{zipFile.replace('.zip', '')}"
                if(not os.path.exists(unzippedDir)):
                    os.mkdir(unzippedDir)
                with ZipFile(f"{actualFolder}/{zipFile}", 'r') as zipper:
                    zipper.extractall(unzippedDir)
            except Exception as e:
                print(f"\nError {e} occured while unzipping the files in {actualFolder}/{zipFile}\n")
 
    def unitFolderProcessing(self, files, folder):
        if(folder not in self.unitTestMap):
            self.unitTestMap[folder] = {"properties": {"zipped": False, "uiparams": False}, "files": {}}
        
        expected_files = [dirfile for dirfile in filter(lambda file: file.startswith('expected_'), files)]
        og_files = [dirfile for dirfile in filter(lambda file: file.endswith('_RequestMessageTemplate.json'), files)]
        if(len(expected_files) > len(og_files)*2): self.unitTestMap[folder]['properties']['uiparams'] = True

        for file in expected_files:
            fileBreakdown = file.split('_')
            fileIsDir = os.path.isdir(f"{self.topFolder}/{folder}/{file}")
            
            if(not fileIsDir):
                filePath = f"{self.topFolder}/{folder}/{'_'.join(fileBreakdown[2:])}"
                transform = fileBreakdown[1]
                if(filePath not in self.unitTestMap[folder]['files']):
                    self.unitTestMap[folder]['files'][filePath] = []
                self.unitTestMap[folder]['files'][filePath].append(transform)
            else:
                self.unitTestMap[folder]['properties']['zipped'] = True
                expected_dir = f"{self.topFolder}/{folder}/{file}"
                expected_dir_files = [expectedFile for expectedFile in os.listdir(expected_dir) if expectedFile.startswith('expected_')]

                for file in expected_dir_files:
                    fileBreakdown = file.split('_')
                    filePath = f"{expected_dir.replace('expected_', '')}/{'_'.join(fileBreakdown[2:])}"
                    transform = fileBreakdown[1]
                    if(filePath not in self.unitTestMap[folder]['files']):
                        self.unitTestMap[folder]['files'][filePath] = []
                    self.unitTestMap[folder]['files'][filePath].append(transform)
        
        self.unitTests -= 1

        if(self.unitTests == 0):
            # setTests(self.unitTestMap, self.ap_rules, self.sp_rules, self.mapping, self.topFolder)
            print(self.unitTestMap)
            

    def topFolderProcessing(self, unitTestFolders):
        for folder in unitTestFolders:
            searchFolder = f"{self.topFolder}/{folder}"

            if(self.checkZip(searchFolder)):
                zippedFolders = [zipFile for zipFile in os.listdir(searchFolder) if zipFile.endswith('.zip')]
                self.extractZipFile(searchFolder, zippedFolders)      
                    
            files = [file for file in os.listdir(searchFolder)]
            self.unitFolderProcessing(files, folder)

    def __init__(self, regressionFoler):
            self.topFolder = regressionFoler
            self.unitTestMap = {}

            folders = [folder for folder in os.listdir(self.topFolder) if os.path.isdir(os.path.join(self.topFolder,folder))]
            self.topFolderProcessing(folders)
            

folderToRegress = sys.argv[1].strip('/')
runTests(folderToRegress)


# "Unit_Test_5": {
#   "properties": {
#     "zipped": True,
#   },
#   "files": {
#      "RegressionTests/Unit_Test_5/Ext_rows(1)/anon.603570-20_12_03 nov 7721.50.xlsx": ["aptrans", "sptrans"],
#      "RegressionTests/Unit_Test_5/Ext_rows(1)/anon.608762-20_11_30nov 4468.65.xlsx": ["aptrans"]
#      } 
#   }
# }
