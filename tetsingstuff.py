import os

# dict = {'Unit_2': 'Pass', 'Unit_1': 'Pass', 'Unit_3': 'Pass', 'Unit_5': 'Pass', 'Unit_4': 'Fail'}

# for key, val in sorted(dict.keys()):
#     print(f"{key}: {val}")


# def trythis():
#     try:
#         val = 8/2
#         print(val)
#     except Exception as e:
#         print(f"Error has occured: {e}")
#     thisdone()

# def thisdone():
#     print("done!")

# trythis()

allfiles = os.listdir('RegressionTests/Unit_Test_4')
og_files = [file for file in allfiles if not (file.startswith(('expected_', 'aptrans_' 'sptrans_')) or file.endswith('_RequestMessageTemplate.json'))]
print(og_files)

for og_file in og_files:
    expected_files = [file for file in allfiles if (file.startswith('expected_') and os.path.splitext(og_file)[0] in file)]
    print(expected_files)
    transformations = []
    for expected_file in expected_files:
        if('prefix' in transformations and 'suffix' in transformations): 
            break
        elif('prefix' in expected_file and 'prefix' not in transformations):
            transformations.append('prefix')
        elif('suffix' in expected_file and 'suffix' not in transformations):
            transformations.append('suffix')
    print(transformations)