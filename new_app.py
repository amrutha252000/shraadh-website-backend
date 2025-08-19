import gspread

gc = gspread.service_account(filename='sb.json')

sh = gc.open("Shraadh Calculator Submissions")

print(sh.sheet1.get('A1'))