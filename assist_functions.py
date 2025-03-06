import pymysql
import mysql.connector

endpoint = 'pollingresults.crqso0moc75j.us-east-2.rds.amazonaws.com'
user = 'noahhhtx'
password = 'MrGame&Watch9!'
database = 'PollingResults'

def query_db(statement):
    con = mysql.connector.connect(
        user=user,
        password=password,
        host=endpoint,
        database=database
    )
    c = con.cursor()
    print(statement)
    c.execute(statement)
    result = c.fetchall()
    con.close()
    return result

def generate_table(header, content, class_=None, id=None, style=None):
    class_str = ""
    id_str = ""
    style_str = ""
    if class_ is not None:
        class_str = " class = \"%s\"" % class_
    if id is not None:
        id_str = " id = \"%s\"" % id
    if style is not None:
        style_str = " style = \"%s\"" % style
    s = "<table" + class_str + id_str + style_str + ">"

    # create row for header
    s += "<tr>"
    for h in header:
        s += "<th>" + h + "</th>"
    s += "</tr>"

    # create entry for each row of content
    for row in content:
        s += "<tr"

        for col in row:
            s += "<td>" + col + "</td>"

        s += "</tr>"

    s += "</table>"

    return s