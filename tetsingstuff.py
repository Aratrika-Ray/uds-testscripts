# keywords = {
#     'Total': ['Total', 'total', 'subtotal', 'sub total', 'sub-total', 'Sub Totals'],
#     'AVC': ["PRSA - AVC", "AVC", "AVEE", "AVCs", "Additional Voluntary Contribution", "(AVC)", "Regular Premium AVC", "AVC Amount", "AVCHALL", "Monthly AVC","AVC Cont", "AVC Cont €", "EE (AVC)", "AVC €", "AVC€"], 
#     'ER': ["employer", "EMPLOYER", "Employer", "Employer Monthly Contribution", "Employer Contribution", "Employer Cont", "E'R", "E'ER", "Regular Premium ER", "Employer Amount", "Value TP Eer", "Monthly ER", "Monthly Employer", "ER Cont", "ER Cont €", "er", "ER", "ER €", "ER€", "ER Contributions", "ER Contribution", "ER Amount", "E'r", "(ER)", "Eer cont", "er value", "ers contribution"], 
#     'EE': ["employee", "Employee", "EMPLOYEE", "Monthly Salary", "Employee Monthly Contribution", "employee monthly contribution", "ees contibution", "ee value", "EE Cont", "EE Cont €", "EE €", "EE€", "Value TP Eee", "E'E", "E'EE", "ee", "EE", "(EE)","Employee Amount", "EE Amount", "Monthly EE", "Monthly Employee", "EE Contribution", "Employee Contribution", "Employee Contributions"]
# }

keywords = {
    'total': ['total'],
    'avc': ['avc', 'additional voluntary contribution'],
    'ee': ['employee', 'ee', 'salary'],
    'er': ['employer', 'er', "e'r", ]
}

print(any(word in '    AVC Cont € '.lower().strip() for word in keywords['avc']))
