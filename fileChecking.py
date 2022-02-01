import os, openpyxl
from glob import glob
import pandas as pd
from totalChecking import totalsChecking

def schemeErrors(exceptionSheets, file):
    for sheet in exceptionSheets:
        excp_df = pd.read_excel(file, sheet_name=sheet)
        n = len(excp_df.index)
        for i in range(0, n):
            if(excp_df.iloc[i, 0].startswith('scheme')):
                return (True, f"{excp_df.iloc[i, 1]} for {file}")
    
    return (False, "NONE")


def checkExceptionSheet(mcol, sheet, file):
    excpdf = pd.read_excel(file, sheet_name=sheet)
    n = len(excpdf.index)
    for i in range(0, n):
        if(mcol in excpdf.iloc[i, 1]):
            return False, "NONE"

    return True, f"{mcol} error not in exception sheet {sheet} which is absent in transformed sheet!"

def exceptionSheetError(transformedSheets, exceptionSheets, file):
    for sheet in transformedSheets:
        transdf = pd.read_excel(file, sheet_name=sheet)

        mandatory_cols = {'unique ID': ['REFNO', 'PPSNO', 'PAYROLL'], 'Contribution': ['EE', 'ER', 'AVC', 'SPEE', 'SPER', 'SPAVC'], 'Surname': 'SURNAME', 'Forename': 'FORENAME'}
        trans_cols = transdf.keys()

        for mcol in mandatory_cols:
            res = any(col.upper() for col in trans_cols if col in mandatory_cols[mcol])
            if(len(transformedSheets) == 1):
                n_exp = len(exceptionSheets)
                if(not res and not n_exp):
                    return True, f"Exception sheet not present for {sheet} in {file}! Mandatory column {mcol} not present."
                elif(not res and n_exp):
                    return checkExceptionSheet(mcol, exceptionSheets[0], file)
            else:
                if(not res and not f"${sheet}" in exceptionSheets):
                    return True, f"Exception sheet not present for {sheet} in {file}! Mandatory column {mcol} not present."
                elif(not res and f"${sheet}" in exceptionSheets):
                    return checkExceptionSheet(mcol, f"${sheet}", file)

    return False, "NONE"


def errorChecking(input_folder):
    input_files = [file for file in os.listdir(input_folder) if file.endswith(('xlsx', 'XLSX')) and not file.startswith(('expected_', 'original_'))]
    with open(f"{input_folder}/regression_report.txt", "w") as f:
        for file in input_files:
            filePath = f"{input_folder}/{file}"
            wb = openpyxl.load_workbook(filePath)
            transformedSheets = [sheet for sheet in wb.sheetnames if not sheet.startswith(('$', '~', '#'))]
            exceptionSheets = [sheet for sheet in wb.sheetnames if sheet.startswith('$')]
            totalSheets = [sheet for sheet in wb.sheetnames if sheet.startswith('#')]

            schemeRes, schemeMsg = schemeErrors(exceptionSheets, filePath)
            f.write(f"Scheme error: {schemeMsg}\n")
            exceptionRes, exceptionMsg = exceptionSheetError(transformedSheets, exceptionSheets, filePath)
            f.write(f"Exception sheet error: {exceptionMsg}\n")
#            if(totalSheets != []):
#                msgs = totalsChecking(filePath, totalSheets)
#                if(msgs != []):
#                    for msg in msgs:
#                        f.write(f"Totaling Check for {msg[0]} - {msg[1]}, {msg[2]}\n")

#print(errorChecking('RegressionTests/Unit_Test_1'))
