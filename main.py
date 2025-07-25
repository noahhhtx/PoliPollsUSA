# written by Noah Harrison

from flask import Flask, request, render_template, Response
import sqlite3
import pymysql
import mysql.connector
import assist_functions
from datetime import datetime
import csv
import io
import os

db_info = {}
db_info["endpoint"] = os.environ.get("endpoint")
db_info["user"] = os.environ.get("user")
db_info["password"] = os.environ.get("password")
db_info["database"] = os.environ.get("database")

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/surveyresults")
def survey_dates():
    statement = "SELECT DISTINCT date FROM survey_results ORDER BY date DESC LIMIT 10;"
    result, desc = assist_functions.query_db(statement, db_info)
    print(result)
    result = list(result)
    rows = []
    print(result)
    for row in result:
        date = row[0]
        date_obj = datetime.strptime(str(date), "%Y%m%d")
        date_str = date_obj.strftime("%B %#d, %Y")
        date_str_url = date_obj.strftime("%Y-%m-%d")
        content = '<a class="intable" style="font-size: 30px; font-weight: bold;" href="/query?keyword=&startdate=' + date_str_url + '&enddate=' + date_str_url + '"/>' + date_str
        print(content)
        rows.append([content])

    output_html = '''
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
                * {
                    font-family: "Roboto", sans-serif;
                }
                table { margin-left: auto;
                    margin-right: auto; }
                .left {float:left;}
                .right {float:right;}
                .center {text-align: center;}
                #keyword { float:right}
                #query_table { 
                    width:350px;
                 }
                #results_table {
                    width:800px;
                }
                .results {
                    border:1px solid black;
                }
                form { text-align:center; }
                h1 { text-align:center; }
                hr.rounded {
                border-top: 5px solid #bbb;
                border-radius: 5px;
                }
                a.intable {
                display: block;
                padding: 50px;
                color: inherit;
                text-decoration: inherit;
                }
                .dates tr:hover {background-color: lightgray;}
                </style>
                <body>'''
    output_html += render_template("header.html")
    output_html += '''<h1 style="text-align:center">Most Recent Survey Results</h1>
        <p style="text-align:center">Click on a date below to see the results of the survey administered on that date.</p>
        <p style="text-align:center">Visit the <a href="/query">Query Page</a> for more specific results.</p>
        '''
    output_html += assist_functions.generate_table(content=rows,
                                                   style="width: 50%; border-spacing: 15px;",
                                                   style_cell="border:2px solid black;text-align:center;width:auto;",
                                                   class_="dates")
    output_html += "</body>"
    return output_html

@app.route("/query", methods =["GET", "POST"])
def query():
    query_string = ""
    if request.method == "POST" or request.method == "GET": # assumes there was in fact an input
        text_box = None
        startdate = None
        enddate = None
        if request.method == "POST":
            text_box = request.form.get("keyword")
            startdate = request.form.get("startdate")
            enddate = request.form.get("enddate")
        else:
            text_box = request.args.get('keyword')
            startdate = request.args.get('startdate')
            enddate = request.args.get('enddate')
        query_strings=[]
        if text_box is not None and text_box != "":
            keywords = []
            for word in text_box.split(" "):
                keywords.append("question LIKE " + "'%" + word + "%'")
            query_strings.append(" AND ".join(keywords))
        if startdate is not None and startdate != "":
            startdate = ("".join([x for x in startdate.split("-")]))
            query_strings.append("date >= " + startdate)
        if enddate is not None and enddate != "":
            enddate = ("".join([x for x in enddate.split("-")]))
            query_strings.append("date <= " + enddate)
        if len(query_strings) > 0:
            query_string = " AND ".join(query_strings)
            query_string = " WHERE " + query_string
    if len(query_string) == 0:
        query_string = " LIMIT 10" # implies nothing was inserted
    output_html = '''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
        * {
            font-family: "Roboto", sans-serif;
        }
        table { margin-left: auto;
            margin-right: auto; }
        .left {float:left;}
        .right {float:right;}
        .center {text-align: center;}
        #keyword { float:right}
        #query_table { 
            width:350px;
         }
        #results_table {
            width:800px;
        }
        .results {
            border:1px solid black;
        }
        form { text-align:center; }
        h1 { text-align:center; }
        hr.rounded {
        border-top: 5px solid #bbb;
        border-radius: 5px;
        }
        .results tr:hover {background-color: lightgray;}
        </style>
        <body>'''
    output_html += render_template("header.html")
    print(startdate)
    print(enddate)
    if ( (startdate is None) or (enddate is None)  ) or ( (len(startdate) == 0) or (len(enddate) == 0) ) or startdate != enddate:
        output_html += '''
            <h1 style="text-align:center">Previous Survey Results</h1>
            <p style="text-align:center">Use this form to query previous survey results.</p>
            <form action="/query" method="post">
                <table id="query_table">
                <tr>
                    <td class="left"> Keyword: </td> 
                    <td class="right"> <input type="text" id="keyword" name="keyword"/> </td>
                </tr>
                <tr>
                    <td class="left"> <label for="startdate">Earliest Poll Begin Date:</label> </td>
                    <td class="right"> <input type="date" id="startdate" name="startdate"/> </td>
                </tr>
                <tr>
                    <td class="left"> <label for="enddate">Latest Poll Begin Date:</label> </td>
                    <td class="right"> <input type="date" id="enddate" name="enddate"/> </td>
                </tr>
                <tr>
                    <td class="center"> <input type="submit" value="Submit"> </td>
                </tr>
                </table>
            </form>
        '''
    else:
        date = datetime.strftime(datetime.strptime(startdate, "%Y%m%d"), "%B %#d, %Y")
        output_html += f'''
        <h1 style="text-align:center">Survey Results for {date}</h1>
        <p style="text-align:center">Visit the <a href="/surveyresults">Survey Results Page</a> to check the results of other surveys.</p>
        <p style="text-align:center">Visit the <a href="/query">Query Page</a> to query other date ranges.</p>
        '''
    statement = ("SELECT date, question, yes, yes_moe, no, no_moe, respondents, note FROM survey_results"
                 + query_string + ";")
    result, desc = assist_functions.query_db(statement, db_info)
    if len(result) == 0:
        output_html+= "<p style=\"text-align:center\"><b>Sorry, no results could be found. Please try another query.</b></p>"
    else:
        rows = []
        for row in result:
            # adjust date
            row = list(row)
            temp = str(row[0])
            temp = temp[4:6] + "/" + temp[6:] + "/" + temp[0:4]
            row[0] = temp
            rows.append(row)
        output_html += assist_functions.generate_table(["Date", "Question", "Yes", "Yes MOE", "No", "No MOE", "n", "Note"],
                                                       rows, "results", "results_table", "text-align: left;", "border:1px solid black;")
        output_html+='''
        <br>
        <form action="/downloadresults" method="post">
            <input type = "hidden" name = "query" value = "''' + statement + '''" />
            <table> 
                <tr>
                    <td class="center"> <input type="submit" value="Download Results"> </td>
                </tr>
            </table>
        </form>'''
    output_html+='''</body>'''
    return output_html
    #return render_template("home.html")

@app.route("/downloadresults", methods=["GET", "POST"])
def download():
    print("Begin of Download Page")
    query = ""
    if request.method == "POST":
        query = request.form.get("query")
    else:
        query = request.args.get("query")
    query = query.replace(" LIMIT 10", "")
    print(query)
    print("End of Download Page")

    result, desc = assist_functions.query_db(query, db_info)

    csv_file = "download.csv"
    output = io.StringIO()
    writer = csv.writer(output)

    column_names = [i[0] for i in desc]
    writer.writerow(column_names)

    writer.writerows(result)

    output.seek(0)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=survey_result.csv"

    return response

@app.route("/trends", methods=["GET", "POST"])
def trend():
    # needs to be finished.
    query_string = ""
    if request.method == "POST" or request.method == "GET": # assumes there was in fact an input
        keywords = ""
        topic = ""
        if request.method == "POST":
            print("POST")
            topic = request.form.get("topic")
            if topic is None:
                topic = "none_selected"
        else:
            print("GET")
            topic = request.args.get('topic')
            if topic is None:
                topic = "none_selected"
        print(topic)
        topic = topic.strip()
        match topic:
            case "Trump Approval":
                keywords = "(question LIKE %TRUMP%) AND (question LIKE %APPROV%)"
            case "Economy Approval":
                keywords = "(question LIKE %ECONOM%) AND ( (question LIKE %APPROV%) OR (question LIKE %OPTIMIS%) )"
    output_html = '''
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
            * {
                font-family: "Roboto", sans-serif;
            }
            table { margin-left: auto;
                margin-right: auto; }
            .left {float:left;}
            .right {float:right;}
            .center {text-align: center;}
            #keyword { float:right}
            #query_table { 
                width:350px;
             }
            #results_table {
                width:800px;
            }
            .results {
                border:1px solid black;
            }
            form { text-align:center; }
            h1 { text-align:center; }
            hr.rounded {
            border-top: 5px solid #bbb;
            border-radius: 5px;
            }
            .results tr:hover {background-color: lightgray;}
            </style>
            <body>'''
    output_html += render_template("header.html")
    return output_html

if __name__ == "__main__":
    app.run(debug=True)
