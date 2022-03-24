import os, sys, subprocess
from UnitTestUDS import setTests

# start the InfoQuery mock server
def mockServerStart():
    cmd = "nohup python3 InfoQueryMock.py > infoqueryserver.txt &"
    servercmd = subprocess.run(cmd, shell=True, stdout = subprocess.PIPE, text=True)
    pid = "pgrep -f Info.py"
    serverpid = subprocess.run(pid, shell=True, stdout = subprocess.PIPE, text=True)

    if(servercmd.returncode == 0 and serverpid.stdout != ''):
        print("\nInfoQuery mock server is running.")
        return 1

    print("\nInfoQuery mock server could not be started.")
    return 0

# stop the InfoQuery mock server
def mockServerStop():
    killserver = subprocess.run('fuser -k 5000/tcp', shell=True, stdout=subprocess.PIPE)
    serverpid = subprocess.run('pgrep -f InfoQueryMock.py', shell=True, stdout=subprocess.PIPE)
    pid = serverpid.stdout.decode('utf-8').split('\n')

    if(killserver.returncode == 0 and len(pid) <= 2):
        print("\nInfoQuery mock server stopped.")
        return 1

    print("\nInfoQuery mock server could not be stopped.")
    return 0

class runTests:
    # set all the rules and column mapping files
    topFolder = 'RegressionTests'
    ap_rules = 'ap_rules.dslr'
    ap_rules_new = 'ap_rules_new.dslr'
    sp_rules = 'sp_rules.dslr'
    sp_rules_new = 'sp_rules_new.dslr'
    mapping = 'column-map1.json'

    # checks for zip files in folder
    def checkZip(self, folder):
        return any(file.endswith('.zip') for file in os.listdir(folder))


    def transformations(self, folderFiles, filename):
        t = 0

        # ap=1, sp=2, ap&sp=3
        for file in folderFiles:
            if("RequestMessageTemplate" in file and filename in file):
                if("ap" in file): t += 1
                if("sp" in file): t += 2

        return t


    def unitFolderProcessing(self, original_folder):
        originalFileFolder = os.path.join(self.topFolder, original_folder)
        folderFiles = os.listdir(originalFileFolder)
        original_files = [file for file in folderFiles if file.startswith('original_')]

        ui_params = any("interleaved_" in file for file in folderFiles)
        self.unitTestMap[original_folder]['properties']['uiparams'] = ui_params

        for file in original_files:
            basename = os.path.splitext(file.replace('original_',''))[0]
            filename = f"{originalFileFolder}/{file}"
            self.unitTestMap[original_folder]['files'][filename] = []

            transcode = self.transformations(folderFiles, basename)
            if(transcode == 3): self.unitTestMap[original_folder]['files'][filename].extend(["aptrans", "sptrans"])
            elif(transcode == 2): self.unitTestMap[original_folder]['files'][filename].append("sptrans")
            elif(transcode == 1): self.unitTestMap[original_folder]['files'][filename].append("aptrans")


    def topFolderProcessing(self, unitTestFolders):
        for folder in unitTestFolders:
            self.unitTestMap[folder] = {"properties": {"zipped": False, "uiparams": False}, "files": {}}
            searchFolder = f"{self.topFolder}/{folder}"

            if(self.checkZip(searchFolder)):
                self.unitTestMap[folder]['properties']['zipped'] = True

            self.unitFolderProcessing(folder)

#        for key in self.unitTestMap.keys():
#           print(f"{key}: {self.unitTestMap[key]}")
        oldClassifierTest, testRes = setTests(self.unitTestMap, self.ap_rules, self.sp_rules, self.mapping, self.topFolder) if self.topFolder ==self.unitTestFolder else setTests({self.unitTestFolder: self.unitTestMap[self.unitTestFolder]}, self.ap_rules, self.sp_rules, self.mapping, self.topFolder)
        if(oldClassifierTest):
            print(f"\33[93mRegression Testing with Old Classifier Finished.Proceeding to Regression Testing with New Classifier\n\033[0;0m")
            newClassifierTest, testRes = setTests(self.unitTestMap, self.ap_rules_new, self.sp_rules_new, self.mapping, self.topFolder, True) if self.topFolder == self.unitTestFolder else setTests({self.unitTestFolder: self.unitTestMap[self.unitTestFolder]}, self.ap_rules_new, self.sp_rules_new, self.mapping, self.topFolder, True)
            if(newClassifierTest):
                for key in testRes.keys():
                    print(f"{key}: {testRes[key]}")
                    sys.__stdout__.write(f"{key}: {testRes[key]}\n")

                print(f"\n\033[1mRegression Testing Complete!\033[0m\n")


    #constructor
    def __init__(self, regressionFolder):
        folderBreakdown = regressionFolder.strip('/').split('/')
        self.topFolder = folderBreakdown[0]
        self.unitTestFolder = folderBreakdown[len(folderBreakdown)-1]
        self.unitTestMap = {}

        folders = [folder for folder in os.listdir(self.topFolder) if folder.startswith('Unit_Test_')]
        self.topFolderProcessing(folders)


if __name__ == "__main__":
    try:
        serverstart = mockServerStart()
        if(serverstart):
            print("\033[1;31m\nUDS Regression Test Suite running. Please wait!\n\033[0;0m")
            folderToRegress = sys.argv[1].strip('/')
            runTests(folderToRegress)
        else: print("The test suite cannot be run!\nYou can try running the server manually - nohup python3 InfoQueryMock.py > infoqueryserver.txt\nOR\nCheck infoqueryserver.txt for errors. \n")
    except (KeyboardInterrupt, SystemExit):
        serverstop = mockServerStop()
        if(serverstop):
            print("\033[1;31m\nRegression Test Suite stopped.\n\033[0;0m")

        sys.exit(0)
