# written by Noah Harrison

from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/query", methods =["GET", "POST"])
def query():
    query_string = ""
    if request.method == "POST": # assumes there was in fact an input
        query_strings=[]
        text_box = request.form.get("keyword")
        if text_box is not None and text_box != "":
            keywords = []
            for word in text_box.split(" "):
                keywords.append("question LIKE " + "'%" + word + "%'")
            query_strings.append(" AND ".join(keywords))
        startdate = request.form.get("startdate")
        if startdate is not None and startdate != "":
            startdate = ("".join([x for x in startdate.split("-")]))
            query_strings.append("date >= " + startdate)
        enddate = request.form.get("enddate")
        if enddate is not None and enddate != "":
            enddate = ("".join([x for x in enddate.split("-")]))
            query_strings.append("date <= " + enddate)
        if len(query_strings) > 0:
            query_string = " AND ".join(query_strings)
            query_string = " WHERE " + query_string
    if len(query_string) == 0:
        query_string = " LIMIT 10" # implies nothing was inserted.
    con = sqlite3.connect("PollingResults.db")
    c = con.cursor()
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
        border-top: 8px solid #bbb;
        border-radius: 5px;
        }
        </style>
        <body>
        <h1>Previous Survey Results</h1>
        <p style="text-align:center">Use this form to query previous survey results. </p>
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
    print(statement)
    result = c.execute(statement).fetchall()
    if len(result) == 0:
        output_html+= "<p style=\"text-align:center\">Sorry, no results could be found. Please try another query.</p>"
    else:
        output_html+='''<table class = "results" id = "results_table" style="text-align: left;">
            <tr class = "results">
                <th class = "results">Date</th>
                <th class = "results">Question</th>
                <th class = "results">Yes</th>
                <th class = "results">Yes MOE</th>
                <th class = "results">No</th>
                <th class = "results">No MOE</th>
                <th class = "results">n</th>
                <th class = "results">Note</th>
            </tr>'''
        for row in result:
            # adjust date
            row = list(row)
            temp = str(row[0])
            temp = temp[4:6] + "/" + temp[6:] + "/" + temp[0:4]
            row[0] = temp
            temp_str = "<tr class = \"results\">"
            for col in row:
                temp_str += "<td class = \"results\">" + str(col) + "</td>"
            temp_str += "</tr>"
            output_html+=temp_str
        output_html+="</table>"
    output_html+='''
    <br>
    <form action="/">
        <input type="submit" value="Home">
    </form>
    </body>'''
    con.close()
    return output_html
    #return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)