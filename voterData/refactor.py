"""
@author: Kristina Bridgwater

This file refactors the precinct data to narrow it down to the final current distribution of the congressional districts
"""
import pandas as pd

def myfunc(dataframe, num):
    dem_x = 0
    rep_x = 0
    oth_x = 0
    tot_x = 0
    df_x = pd.DataFrame(dataframe.loc[dataframe['congr_d'] == num])
    for ind in df_x.index:
        if df_x['party'][ind] == 'DEMOCRAT':
            dem_x += df_x['totalv'][ind]
        elif df_x['party'][ind] == 'REPUBLICAN':
            rep_x += df_x['totalv'][ind]
        elif df_x['party'][ind] == 'GREEN':
            oth_x += df_x['totalv'][ind]
        elif df_x['party'][ind] == 'LIBERTARIAN':
            oth_x += df_x['totalv'][ind]
        elif df_x['party'][ind] == 'UNAFFILIATED':
            oth_x += df_x['totalv'][ind]
        elif df_x['party'][ind] == 'OTHER PARTIES':
            oth_x += df_x['totalv'][ind]
        tot_x += df_x['totalv'][ind]
    dem_p = ((dem_x/tot_x)*100)
    rep_p = ((rep_x/tot_x)*100)
    oth_p = ((oth_x/tot_x)*100)
    listx = []
    listx.append(dem_p)
    listx.append(rep_p)
    listx.append(oth_p)
    maxc = max(listx)
    if maxc == dem_p:
        color = "blue"
    elif maxc == rep_p:
        color = "red"
    else:
        color = "yellow"

    listx.append(color)
    listx.append(num)

    return listx


df = pd.read_csv('Official by Party and Precinct.csv')

newrow = []
allrows = []

for i in range(len(df)):
    congr_d = df.loc[i, "CONGRESSIONAL_DISTRICT_CODE"]
    newrow.append(congr_d)
    prec = df.loc[i, "PRECINCT"]
    newrow.append(prec)
    party = df.loc[i, "PARTY"]
    newrow.append(party)
    totalv = (df.loc[i, "POLLS"]) + (df.loc[i, "EARLY_VOING"]) + (df.loc[i, "ABSENTEE"]) + (df.loc[i, "PROVISIONAL"])
    newrow.append(totalv)
    allrows.append(newrow)
    newrow = []
print(allrows)

newdf = pd.DataFrame(allrows, columns=['congr_d', 'precinct', 'party', 'totalv'])
newdf.to_csv(r'/Users/kristinabridgwater/Documents/cmsc447proj_kb/voterData/new_csv.csv', index=False, header=True)


df_c = pd.read_csv('new_csv.csv')
cdata = []

df_01 = myfunc(df_c, 1)
cdata.append(df_01)
df_02 = myfunc(df_c, 2)
cdata.append(df_02)
df_03 = myfunc(df_c, 3)
cdata.append(df_03)
df_04 = myfunc(df_c, 4)
cdata.append(df_04)
df_05 = myfunc(df_c, 5)
cdata.append(df_05)
df_06 = myfunc(df_c, 6)
cdata.append(df_06)
df_07 = myfunc(df_c, 7)
cdata.append(df_07)
df_08 = myfunc(df_c, 8)
cdata.append(df_08)

finaldf = pd.DataFrame(cdata, columns=['dem', 'rep', 'oth', 'color', 'c_district'])
finaldf.to_csv(r'/Users/kristinabridgwater/Documents/cmsc447proj_kb/voterData/final_csv.csv', index=False, header=True)

