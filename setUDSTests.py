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
                unzippedDir = f"{actualFolder}/original_{zipFile.replace('.zip', '')}"
                if(not os.path.exists(unzippedDir)):
                    os.mkdir(unzippedDir)
                with ZipFile(f"{actualFolder}/{zipFile}", 'r') as zipper:
                    zipinfos = zipper.infolist()
                    for zipinfo in zipinfos:
                        zipinfo.filename = f"original_{zipinfo.filename}"
                    zipper.extractall(unzippedDir, zipinfos)
            except Exception as e:
                print(f"\nError {e} occured while unzipping the files in {actualFolder}/{zipFile}\n")
 

    def fileProcessing(self, folder, original_file, expected_files):
        searchFolder = os.path.join(self.topFolder, folder)
        fileIsDir = os.path.isdir(os.path.join(searchFolder, original_file)) 

        if(any('interleaved_' in file or 'new_' in file for file in expected_files)):
            self.unitTestMap[folder]['properties']['uiparams'] = True
           
        if(not fileIsDir):
            filePath = f"{searchFolder}/{original_file}"
            
            ap = any('aptrans_' in file for file in expected_files)
            sp = any('sptrans_' in file for file in expected_files)
                
            if(filePath not in self.unitTestMap[folder.split('/')[0]]['files']):
                transformations = []
                if(ap): transformations.append('aptrans')
                if(sp): transformations.append('sptrans')
                self.unitTestMap[folder.split('/')[0]]['files'][filePath] = transformations
        else:
            for file in expected_files:
                expected_folder = f"{folder}/{file}"
                unzipped_folder = expected_folder.replace('expected_', 'original_')
                self.unitFolderProcessing(unzipped_folder, expected_folder)          
        

    def unitFolderProcessing(self, original_folder, expected_folder):
        originalFileFolder = os.path.join(self.topFolder, original_folder)
        expectedFileFolder = os.path.join(self.topFolder, expected_folder)
        original_files = [file for file in os.listdir(originalFileFolder) if file.startswith('original_')]

        for original_file in original_files:
            expected_files = [file for file in os.listdir(expectedFileFolder) if (file.startswith('expected_') and os.path.splitext(original_file.replace('original_',''))[0] in file)]
            self.fileProcessing(original_folder, original_file, expected_files)         


    def topFolderProcessing(self, unitTestFolders):
        for folder in unitTestFolders:
            self.unitTestMap[folder] = {"properties": {"zipped": False, "uiparams": False}, "files": {}}
            searchFolder = f"{self.topFolder}/{folder}"

            if(self.checkZip(searchFolder)):
                self.unitTestMap[folder]['properties']['zipped'] = True
                zippedFolders = [zipFile for zipFile in os.listdir(searchFolder) if zipFile.endswith('.zip')]
                self.extractZipFile(searchFolder, zippedFolders)      
                    
            self.unitFolderProcessing(folder, folder)
        
        setTests(self.unitTestMap, self.ap_rules, self.sp_rules, self.mapping, self.topFolder)
        for key in self.unitTestMap.keys():
            print(f"{key}: {self.unitTestMap[key]}")


    def __init__(self, regressionFoler):
        self.topFolder = regressionFoler
        self.unitTestMap = {}

        folders = [folder for folder in os.listdir(self.topFolder)]
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
