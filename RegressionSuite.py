import os
from threading import Thread
import pandas as pd
from openpyxl import load_workbook
from time import time
from FileChecking import errorChecking

threadRes = {'error': [''], 'comparison': [''], 'color': ['']}

# checks if transformed and expected file column names are same
def check_same_cols(df1, df2):
    return all(df1.columns == df2.columns)

# checks if transformed and expected file column values are same
def compare_two_dfs(df_ideal, df_transformed, columns_to_ignore=[]):
    if_same_cols = check_same_cols(df_ideal, df_transformed)
    df_ideal = df_ideal.fillna(0)
    df_transformed = df_transformed.fillna(0)
    
    if if_same_cols:
        col_set = set(df_ideal.columns) - set(columns_to_ignore)

        for col in col_set:
            temp = df_ideal[col] != df_transformed[col]

            if sum(temp) != 0:
                return (False, f"Mismatch in Column {col}\n{df_ideal[temp][col]} is not equal to \n{df_transformed[temp][col]}")

        return True, "NONE"

# get all sheetnames which start with $/~/#
def get_comparable_sheetnames(workbook):
    return [
        sheetname
        for sheetname in workbook.sheetnames
        if not (
            sheetname.startswith("$")
            or sheetname.startswith("~")
            or sheetname.startswith("#")
        )
    ]

# checks if transformed and expected files have the same sheets
def if_same_sheets(wb1, wb2):
    wb1_sheets = get_comparable_sheetnames(wb1)
    wb2_sheets = get_comparable_sheetnames(wb2)
    return set(wb1_sheets) == set(wb2_sheets), wb1_sheets

# check if the transformed file sheets are correctly coloured and macthes the expected file sheets
def if_same_color_sheets(wb1, wb2):
    n = len(wb2.worksheets)   
    sheetnames = [name for name in wb2.sheetnames]
    sheetcolors = [sheet.sheet_properties.tabColor for sheet in wb2.worksheets]
    msg = ""
    
    for i in range(0, n):           
        if((sheetnames[i].startswith('~') or sheetnames[i].startswith('#')) and not (sheetcolors[i] == None or sheetcolors[i].rgb == 'FFFFFFFF')):
            msg += f"\n{sheetnames[i]} does not have the appropriate color coding"
        elif(sheetnames[i].startswith('$') and not (sheetcolors[i].rgb == 'FFFF0000')):
            msg += f"\n{sheetnames[i]} does not have the appropriate color coding"
        elif(sheetnames[i].startswith(r'\W') and not (sheetcolors[i].rgb == 'FFFFFF00')):
            msg += f"\n{sheetnames[i]} does not have the appropriate color coding"
    
    return (True, "NONE") if msg == "" else (False, msg)

# starts the comparison of the transformed and expecetd files in a unit test folder
def compare_excel_files(transformed_file, ideal_folder):
    print('2. Comparing expected and transformed files')
    cur_sheet = None
    try:
        # checks if the expected file exists for a transformed file
        exists, ideal_file = os.path.exists(f"{ideal_folder}/expected_{os.path.basename(transformed_file)}"), f"{ideal_folder}/expected_{os.path.basename(transformed_file)}"
        if(exists):
            wb1 = load_workbook(ideal_file)
            wb2 = load_workbook(transformed_file)

            same_sheets, sheets = if_same_sheets(wb1, wb2)
            sheet_color, sheet_color_message = if_same_color_sheets(wb1, wb2)
            if same_sheets:
                sheeterr = []
                for sheet in sheets:
                    cur_sheet = sheet
                    df_ideal = pd.read_excel(ideal_file, sheet_name=sheet)
                    df_transformed = pd.read_excel(transformed_file, sheet_name=sheet)
                    result, message = compare_two_dfs(df_ideal, df_transformed) if not (df_ideal.empty and df_transformed.empty) else True, "NONE"

                    sheeterr.append(message)
                    sheeterr.sort()
                    threadRes['comparison'].append(sheeterr[0])
            else:
                threadRes["comparison"].append(f"Sheets in the Excel are not same\t {wb1.sheetnames}!={wb2.sheetnames}")
            threadRes['color'].append(f"{sheet_color_message}")
        else:
            threadRes["comparison"].append(f"{ideal_file} not found in {ideal_folder}")
            threadRes['color'].append("Can't check for color coding of sheets due to missng expecetd file")
    except Exception as e:
        threadRes["comparison"].append(f"Exception Occurred in File={transformed_file}={e} in sheet={cur_sheet}")
        threadRes['color'].append("Can't check for color coding of sheets due to exception")

# start regression test for unit test
def regressionTest(ideal_folder, input_folder):
    # all transformed files
    comparison_files = [file for file in os.listdir(input_folder) if file.endswith(('xlsx', 'XLSX')) and not file.startswith(('expected_', 'original_'))]
    total = len(comparison_files)
    total_correct = 0
    start_time = time()

    with open(f"{input_folder}/regression_report.txt", "w") as f:
        for file in comparison_files:
            try:
                print(file)
                f.write(f"FILE -- {os.path.basename(file)}\n")
                thread_error = Thread(target=errorChecking, args=(f"{input_folder}/{file}", threadRes))
                thread_comparison = Thread(target=compare_excel_files, args=(f"{input_folder}/{file}", ideal_folder))
                threads = [thread_error, thread_comparison]
                
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()

                f.write(threadRes["error"][-1])
                f.write(f"Color Coding Error: {threadRes['color'][-1]}\nFile Comparison Error:{threadRes['comparison'][-1]}\n\n")
                total_correct += 1 if (threadRes['color'][-1] == 'NONE' and threadRes["comparison"][-1] == 'NONE') else 0

            except Exception as e:
                f.write(e)
        
        f.write(f"Test results for {input_folder}-\n")
        f.write(f"TotalFiles\tPassed\tFailed\n")
        f.write(f"{total}\t\t{total_correct}\t{total-total_correct}")
        f.write(f"\n\nTotal time taken={time()-start_time} seconds\n")
    
    return (total_correct == total)
