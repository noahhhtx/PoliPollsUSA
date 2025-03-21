import pandas as pd
import gspread as gsp
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pymysql
import mysql.connector

endpoint = 'pollingresults.crqso0moc75j.us-east-2.rds.amazonaws.com'
user = 'noahhhtx'
password = 'MrGame&Watch9!'
database = 'PollingResults'

def process_zips(c, zip_codes):
    for i in zip_codes:
        zip = str(i)
        if len(zip) < 5:
            continue
        elif len(zip) > 5:
            zip = zip[0:5]
        if not zip.isdigit():
            continue
        cur = c.cursor()
        cur.execute("""INSERT INTO zip_codes (zip, count)
        VALUES (%s, 1)
        ON DUPLICATE KEY UPDATE count=count+1;""", (int(zip)))
        con.commit()

def change_agree(s):
    if "Agree" in s:
        return "Yes"
    elif "Disagree" in s:
        return "No"
    else:
        return s

def count_nones(x):
    i = 0
    k = None
    for j in x:
        if j is None:
            i+=1
        if j is not None:
            k = j
    return i, k

def compute_conf_interval(responses, response):
    z_val = 1.96 # 95% conf. interval, might want to change later
    no_responses = len(responses)
    no_response = len([x for x in responses if x == response])
    proportion = 1.0 * no_response / no_responses
    alt_proportion = 1 - proportion
    MOE = z_val * np.sqrt( 1.0 * (proportion * alt_proportion) / no_responses )
    return (np.round(100*proportion,4), np.round(100*(MOE),4))

def compute_metrics(df, question, responses, dc):
    df_copy = df.copy(deep=True)

    demographic_string = ""
    for i in range(len(dc)):
        if dc[i] is None:
            continue
        df_copy = df_copy[df_copy[df_copy.columns[i]]==dc[i]]
        if len(df_copy) <= 1:
            return
        demographic_string += (dc[i] + " ")
    demographic_string = demographic_string.strip()
    if demographic_string == "":
        demographic_string = "Overall"

    print(demographic_string)

    props = []

    q = df_copy.iloc[:, question]
    for r in responses:
        prop, prop_moe = compute_conf_interval(q, r)
        print(r, prop, prop_moe)
        props.extend([prop,prop_moe])
    print()
    return props, demographic_string

gc = gsp.oauth()

print("Obtaining titles")
titles = [sh.title for sh in gc.openall() if sh.title.endswith("PoliPollsUSA")]
print(titles)

date = input("Select the date of the desired poll: ")
date += " PoliPollsUSA"

sh = gc.open(date).sheet1
print("Sheet opened")
data = sh.get_all_values()
cols = data[0]
data = data[1:]

con = mysql.connector.connect(
    user=user,
    password=password,
    host=endpoint,
    database=database
)

df = pd.DataFrame(data)
df.columns = cols

df = df.drop("On a scale of 1-10, with 1 being bad and 10 being good, how confident are you in the stability of the U.S. economy under Donald Trump?", axis=1)

print(df)

print(len(df), "rows before preprocessing")

# Preprocessing Part 1: We want only responses captured within a week of the first response
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
earliest_response = df["Timestamp"][0]
print(earliest_response)
latest_response = earliest_response + datetime.timedelta(weeks=1)
print(latest_response)
df = df[df["Timestamp"] <= latest_response]
df = df.drop("Timestamp", axis=1)

earliest_response_int = int(earliest_response.strftime("%Y%m%d"))

# Preprocessing Part 2: Removing NA values
df = df.replace("", np.nan)
df = df.dropna()

starting_point = 3

if "ZIP Code" in df.columns[starting_point]:
    zips = df[df.columns[starting_point]].values.tolist()
    process_zips(con, zips)
    starting_point = 4

# Preprocessing Part 3: Setting "Agree" and "Disagree" responses to "Yes" and "No"
for i in range(starting_point, len(df.columns)):
    df[df.columns[i]] = df[df.columns[i]].apply(change_agree)

print(df.info())
print(len(df), "rows after preprocessing")

n_respondents = len(df)

note = input("Notes about survey: ")

print()

# Now to generate the statistics...

genders = [None] + list(pd.unique(df[df.columns[0]]))
races = [None] + list(pd.unique(df[df.columns[1]]))
parties = [None] + list(pd.unique(df[df.columns[2]]))

print(genders)
print(races)
print(parties)

overall_question_data = []
col_names=None

specific_data_for_convenience = {}

for question in range(starting_point, len(df.columns)):

    specific_data_for_convenience[df.columns[question]] = {"Gender": {"Yes":[], "No":[], "Names":[]},
                                                           "Party": {"Yes":[], "No":[], "Names":[]},
                                                           "Race": {"Yes":[], "No":[], "Names":[]}}

    answers = ["Yes", "No"]
    col_names = ["Question"]
    current_question_data = [df.columns[question]]
    print(df.columns[question])

    # Segment by demographics
    for gender in genders:
        for race in races:
            for party in parties:
                test = compute_metrics(df,question,answers, [gender,race,party])
                if test is None:
                    continue
                results, demo_string = test[0], test[1]
                current_question_data.extend(results)
                i, k = count_nones([gender, race, party])
                for ans in answers:
                    a = demo_string + " " + ans
                    b = a + " Margin of Error"
                    col_names.extend([a,b])
                if i == 2 and k is not None:
                    if k in genders:
                        specific_data_for_convenience[df.columns[question]]["Gender"]["Yes"].append(results[0])
                        specific_data_for_convenience[df.columns[question]]["Gender"]["No"].append(results[2])
                        specific_data_for_convenience[df.columns[question]]["Gender"]["Names"].append(k)
                    elif k in parties:
                        specific_data_for_convenience[df.columns[question]]["Party"]["Yes"].append(results[0])
                        specific_data_for_convenience[df.columns[question]]["Party"]["No"].append(results[2])
                        specific_data_for_convenience[df.columns[question]]["Party"]["Names"].append(k)
                    else:
                        specific_data_for_convenience[df.columns[question]]["Race"]["Yes"].append(results[0])
                        specific_data_for_convenience[df.columns[question]]["Race"]["No"].append(results[2])
                        specific_data_for_convenience[df.columns[question]]["Race"]["Names"].append(k)
                if demo_string is not None and demo_string == "Overall":
                    cursor = con.cursor()
                    cursor.execute("""INSERT INTO survey_results (date, question, yes, yes_moe, no, no_moe, respondents, note) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE date=%s, question=%s, yes=%s, yes_moe=%s, no=%s, no_moe=%s, respondents=%s, note=%s;""", (earliest_response_int, df.columns[question], results[0],
                                                  results[1], results[2], results[3], n_respondents, note, earliest_response_int, df.columns[question], results[0], results[1], results[2], results[3], n_respondents, note))
                    con.commit()


    overall_question_data.append(current_question_data)

    print()

overall_results = pd.DataFrame(overall_question_data, columns=col_names)
print(overall_results)

print(specific_data_for_convenience)

for question in specific_data_for_convenience:
    for indicator in specific_data_for_convenience[question]:
        X = specific_data_for_convenience[question][indicator]["Names"]
        yes = specific_data_for_convenience[question][indicator]["Yes"]
        no = specific_data_for_convenience[question][indicator]["No"]
        X_axis = np.arange(len(X))

        plt.bar(X_axis - 0.2, yes, 0.4, label='Yes')
        plt.bar(X_axis + 0.2, no, 0.4, label='No')

        plt.xticks(X_axis, X)
        plt.xlabel(indicator)
        plt.ylabel("Percent")
        plt.title(question + "\nBy " + indicator, fontsize=10)
        plt.xticks(fontsize=7.5)
        plt.ylim(0,100)
        plt.legend()
        plt.show()

    #overall_results.to_csv("test.csv")

con.close()
