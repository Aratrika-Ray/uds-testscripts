from numpy import NaN
import pandas as pd
import openpyxl

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
            row = df.iloc[i]
            cells = [type(cell) for cell in row]
            if(cells.count(float) > m-1):
                df = df.drop(df.index[i])
        
        df = df.fillna('NAN')

        return df
 

    def calculateTotals(self, df):
        n = len(df.columns)
        try:
            for i in range(0, n):
                col = df.iloc[:,i]
                cells = [cell for cell in col]

                for key in self.keywords.keys():
                    if(any(type(cell)==str and word in cell.lower().strip() for word in self.keywords[key] for cell in cells)):
                        self.matrix.append(cells)
                        
            m, i = len(self.matrix), 0
            while(i < m):
                if(not any(type(cell)==float for cell in self.matrix[i])):
                    self.matrix.pop(i)
                m -= 1

            
            n = len(self.matrix[0])-1

            for row in self.matrix:
                sum = 0
                for i in range(n, -1, -1):
                    if(type(row[i]) == float or type(row[i]) == int):
                        sum += row[i]
                    elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["avc"])):
                        self.sumtotal["AVC"].append(round(sum, 2)) if round(sum, 2) not in self.sumtotal['AVC'] else None
                        self.matrix = []
                        break
                    elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["er"])):
                        self.sumtotal["ER"].append(round(sum, 2)) if round(sum, 2) not in self.sumtotal['ER'] else None
                        self.matrix = []
                        break
                    elif(type(row[i]) == str and any(word in row[i].lower().strip() for word in self.keywords["ee"])):
                        self.sumtotal["EE"].append(round(sum, 2)) if round(sum, 2) not in self.sumtotal['EE'] else None
                        self.matrix = []
                        break
        except Exception as e:
            print(f"Error {e} occured during total checking.")

    
    def compareTotals(self, filepath, sheet):
        dft = pd.read_excel(filepath, sheet_name=sheet)
        keys = [key for key in dft.keys() if not 'Unnamed: ' in key]
                
        if(len(err) != 0): err.clear()
        for i in range(0, len(keys)):
            err.append((keys[i], f"total sheet - {dft.iloc[0][i]}", f"calculated - {self.sumtotal[keys[i]]}"))
        
    def __init__(self, filepath, sheet):
        df = pd.read_excel(filepath, sheet_name=sheet.replace('#', '~'))
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all')
        print(df)

        self.keywords = {
            'total': ['total'],
            'avc': ['avc', 'additional voluntary contribution'],
            'ee': ['employee', 'ee', 'salary'],
            'er': ['employer', 'er', "e'r", ]
        }
        self.sumtotal = {'AVC': [], 'ER': [], 'EE': []}
        
        self.matrix = []

        n = len(df.columns)
        self.df = self.dfProcessing(n, df)
        self.df = self.postDFProcessing(self.df)
        print(self.df)
        self.calculateTotals(self.df)

        self.compareTotals(filepath, sheet)


def totalsChecking(filePath, totalSheets):
    for sheet in totalSheets:
        ExtraneousRowFix(filePath, sheet)
    return err

file1 = 'testingfiles/aptrans_anon.Copy_of_Irish_Life_Transfer_letter.xlsx'
file2 = 'testingfiles/aptrans_anon.603570-20_12_03 nov 7721.50.xlsx'
file3 = 'testingfiles/aptrans_anon.602447PRSA_-_Exec_0720 (2).xlsx'
file4 = 'testingfiles/aptrans_HiddenColumn.xlsx'
file5 = 'testingfiles/Trans_anon.Copy of 603992 Monthly Pension Breakdown Millicent Pharma Ltd July 2020 upload.xlsx'
file6 = 'testingfiles/aptrans_anon.603520Irish_Life_Pension_Report_July_2020.xlsx'
wb = openpyxl.load_workbook(file1)
totalSheets = [sheet for sheet in wb.sheetnames if sheet.startswith('#')]
msgs = totalsChecking(file1, totalSheets)
print(msgs)




 # self.keywords = {'Total': ['Total', 'total', 'subtotal', 'sub total', 'sub-total', 'Sub Totals'],
        #             'AVC': ["PRSA - AVC", "AVC", "AVEE", "AVCs", "Additional Voluntary Contribution", "(AVC)", "Regular Premium AVC", "AVC Amount", "AVCHALL", "Monthly AVC","AVC Cont", "AVC Cont €", "EE (AVC)", "AVC €", "AVC€"], 
        #             'ER': ["employer", "EMPLOYER", "Employer", "Employer Monthly Contribution", "Employer Contribution", "Employer Cont", "E'R", "E'ER", "Regular Premium ER", "Employer Amount", "Value TP Eer", "Monthly ER", "Monthly Employer", "ER Cont", "ER Cont €", "er", "ER", "ER €", "ER€", "ER Contributions", "ER Contribution", "ER Amount", "E'r", "(ER)", "Eer cont", "er value", "ers contribution"], 
        #             'EE': ["employee", "Employee", "EMPLOYEE", "Monthly Salary", "Employee Monthly Contribution", "employee monthly contribution", "ees contibution", "ee value", "EE Cont", "EE Cont €", "EE €", "EE€", "Value TP Eee", "E'E", "E'EE", "ee", "EE", "(EE)","Employee Amount", "EE Amount", "Monthly EE", "Monthly Employee", "EE Contribution", "Employee Contribution", "Employee Contributions"]}

   
    # def dfProcessing1(self, df):
    #     k = len(df.index)
    #     dfend = df.iloc[k-6:]
    #     dfend = dfend.dropna(thresh=4, axis=0)
    #     df = df.drop(df.index[k-6:])
    #     df = df.append(dfend)

    #     return df.fillna('NAN')

    # def dfProcessing2(self, df):
    #     df = df.fillna('NAN')
    #     col2 = df.iloc[:, 1]
    #     cells = [cell for cell in col2]
    #     n = len(cells)
    #     cells.reverse()
    #     index_f = cells.index('NAN')
    #     if(index_f < n/2):
    #         for i in range(index_f, n):
    #             if(cells[i]=='NAN' and not cells[i+1]=='NAN' and cells[i-1]=='NAN'):
    #                 index_l= i
    #                 df = df.drop(df.index[n-index_l-1:n-index_f+1])
    #                 break
    #     return df