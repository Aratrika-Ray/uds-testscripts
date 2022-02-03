import os
import sys
from zipfile import ZipFile
from UnitTestUDS import setTests
from RabbitConn import getrabbitmqconn

class runTests:
    topFolder = 'RegressionTests'
    ap_rules = 'ap_rules.dslr'
    ap_rules_new = 'ap_rules_new.dslr'
    sp_rules = 'sp_rules.dslr'
    sp_rules_new = 'sp_rules_new.dslr'
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

#        for key in self.unitTestMap.keys():
#            print(f"{key}: {self.unitTestMap[key]}")
        oldClassifierTest, testRes = setTests(self.unitTestMap, self.ap_rules, self.sp_rules, self.mapping, self.topFolder) if self.topFolder == self.unitTestFolder else setTests({self.unitTestFolder: self.unitTestMap[self.unitTestFolder]}, self.ap_rules, self.sp_rules, self.mapping, self.topFolder)
        if(oldClassifierTest):
            print(f"\33[93mRegression Testing with Old Classifier Finished\nProceeding to Regression Testing with New Classifier\033[0;0m")
            newClassifierTest, testRes = setTests(self.unitTestMap, self.ap_rules, self.sp_rules, self.mapping, self.topFolder, True) if self.topFolder == self.unitTestFolder else setTests({self.unitTestFolder: self.unitTestMap[self.unitTestFolder]}, self.ap_rules, self.sp_rules, self.mapping, self.topFolder, True)
            if(newClassifierTest):
                sys.stdout = sys.__stdout__
                for key in testRes.keys():
                    print(f"{key}: {testRes[key]}")
                
                print(f"\n\033[1mRegression Testing Complete!\033[0m\n")


    def __init__(self, regressionFolder):
        folderBreakdown = regressionFolder.strip('/').split('/')
        self.topFolder = folderBreakdown[0]
        self.unitTestFolder = folderBreakdown[len(folderBreakdown)-1]
        self.unitTestMap = {}

        folders = [folder for folder in os.listdir(self.topFolder) if folder.startswith('Unit_Test_')]
        self.topFolderProcessing(folders)

def main():
    try:
        print("\033[1;31m\nUDS Regression Test Suite running. Please wait!\n\033[0;0m")
        folderToRegress = sys.argv[1].strip('/')
        runTests(folderToRegress)
    except KeyboardInterrupt:
        conns = getrabbitmqconn()
        for conn in conns: 
           conns[conn].close()
        print("\033[1;31m\nPlease TERMINATE the session before running the Regression Test Suite again!\n\033[0;0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
