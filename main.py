# written by Noah Harrison

from flask import Flask, request, render_template
import sqlite3
import pymysql
import mysql.connector
import assist_functions

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

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
        </style>
        <body>'''
    output_html += render_template("header.html")
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
            </td>
            </table>
        </form>
    '''
    statement = ("SELECT date, question, yes, yes_moe, no, no_moe, respondents, note FROM survey_results"
                 + query_string + ";")
    result = assist_functions.query_db(statement)
    if len(result) == 0:
        output_html+= "<p style=\"text-align:center\">Sorry, no results could be found. Please try another query.</p>"
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
    </body>'''
    return output_html
    #return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
