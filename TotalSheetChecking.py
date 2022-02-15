from numpy import NaN
import pandas as pd
import openpyxl
from threading import Thread

err = []

class ExtraneousRowFix:
    def dfProcessing(self, n, df):
        df.loc[-1] = df.columns.values
        df.index = df.index + 1
        df = df.sort_index()

        totalindex = []

        for i in range(0, n):
            col = df.iloc[:, i]
            cells = [cell for cell in col]
            for j, val in enumerate(cells):
                if(type(val)==str and any(word in val.lower().strip() for word in self.keywords["total"])):
                    totalindex.append((i,j))

        for index in totalindex:
            if(index[0] >= n/2):
                df = df.iloc[:, 0:index[0]]
            else:
                df = df.iloc[:index[1], :]
        return df


    def postDFProcessing(self, df):
        n = len(df.index)-1
        m = len(df.columns)
        for i in range(n, -1, -1):
            row = [val for val in df.iloc[i]]
            typearr = [type(val) for val in row]
            nancount = row.count(NaN)
            numbercount = m - nancount
            if(nancount >= numbercount and typearr.count(str) == 0 ):
                df = df.drop(df.index[i])

        df = df.fillna('NAN')

        return df


    def collectRows(self, df):
        try:
            n = len(df.columns)
            threads = []
            for i in range(0, n):
                col = df.iloc[:,i]
                cells = [cell for cell in col]
                for key in self.keywords.keys():
                    if(any(word in cell.lower().strip() for word in self.keywords[key] for cell in cells if type(cell)==str)):
                        self.matrix.append(cells)
                        
            m, i = len(self.matrix), 0
            while(i < m):
                if(not any(type(cell)==float or type(cell)==int for cell in self.matrix[i])):
                    self.matrix.pop(i)
                m -= 1

            n = len(self.matrix[0])-1

            for row in self.matrix:
                threads.append(Thread(target=self.calculateTotal, args=(n, row)))

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        except Exception as e:
            print(f"Error {e} occured during total checking.")


    def calculateTotal(self, n, row):
        try:
            sum = 0
            for i in range(n, -1, -1):
                if(type(row[i]) == float or type(row[i]) == int):
                    sum += row[i]
                elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["avc"])):
                    self.sumtotal["AVC"].append(round(sum, 2)) if round(
                        sum, 2) not in self.sumtotal['AVC'] else None
                    self.matrix = []
                    break
                elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["er"])):
                    self.sumtotal["ER"].append(round(sum, 2)) if round(
                        sum, 2) not in self.sumtotal['ER'] else None
                    self.sumtotal["SPER"].append(round(sum, 2)) if round(
                        sum, 2) not in self.sumtotal['SPER'] else None
                    self.matrix = []
                    break
                elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["ee"])):
                    self.sumtotal["EE"].append(round(sum, 2)) if round(
                        sum, 2) not in self.sumtotal['EE'] else None
                    self.sumtotal["SPEE"].append(round(sum, 2)) if round(
                        sum, 2) not in self.sumtotal['SPEE'] else None
                    self.matrix = []
                    break
        except Exception as e:
            print(f"Error {e} occured during total calculation.")

    
    def compareTotals(self, filepath, sheet):
        dft = pd.read_excel(filepath, sheet_name=sheet)
        keys = [key for key in dft.keys() if not 'Unnamed: ' in key]
                
        if(len(err) != 0): err.clear()
        for i in range(0, len(keys)):
            err.append((keys[i],  f"total sheet = {dft.iloc[0][i]}", f"calculated values = {dft.iloc[0][i] if dft.iloc[0][i] in self.sumtotal[keys[i]] else self.sumtotal[keys[i]]}"))
        
    def __init__(self, filepath, sheet):
        df = pd.read_excel(filepath, sheet_name=sheet.replace('#', '~'))
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all', axis=0)

        self.keywords = {
            'total': ['total'],
            'avc': ['avc', 'additional voluntary contribution'],
            'ee': ['employee', 'ee', 'salary'],
            'er': ['employer', 'er', "e'r", ]
        }
        self.sumtotal = {'AVC': [], 'ER': [], 'SPER': [], 'EE': [], 'SPEE': []}
        
        self.matrix = []

        n = len(df.columns)
        self.df = self.dfProcessing(n, df)
        self.df = self.postDFProcessing(self.df)
        self.collectRows(self.df)
        self.compareTotals(filepath, sheet)


def totalsChecking(filePath, totalSheets, threadRes):
    for sheet in totalSheets:
        ExtraneousRowFix(filePath, sheet)
    threadRes['total'] = err


def miroTableChecking(filePath, totalSheets, transformedSheets, threadRes):
    threadRes['miro'] = "NONE"
    if(len(transformedSheets) == 1):
        transdf = pd.read_excel(filePath, sheet_name=transformedSheets[0])
        if('ISSUES FOUND' in transdf.columns and not transdf['ISSUES FOUND'].isna().all()):
            totaldf = pd.read_excel(filePath, sheet_name=totalSheets[0])
            if(not len(totaldf.index) > 10):
                threadRes['miro'] = f"Scheme Number present but Miro Table not found in total sheet: {totalSheets[0]}"
    else:
        for sheet in totalSheets:
            transdf = pd.read_excel(
                filePath, sheet_name=sheet.replace('#', ''))
            if('ISSUES FOUND' in transdf.columns and not transdf['ISSUES FOUND'].isna().all()):
                totaldf = pd.read_excel(filePath, sheet_name=sheet)
                if(not len(totaldf.index) > 10):
                    threadRes['miro'] = f"Scheme Number present but Miro Table not found in total sheet: {sheet}"
