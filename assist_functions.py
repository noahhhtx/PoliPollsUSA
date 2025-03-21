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

def generate_table(header=[], content=[], class_=None, id=None, style=None, style_cell=None, style_header=None, cols=None):
    count_cols = False
    if cols is not None:
        count_cols = True
    counter = 0
    class_str = ""
    id_str = ""
    style_str = ""
    style_cell_str = ""
    style_header_str = ""
    if class_ is not None:
        class_str = " class = \"%s\"" % class_
    if id is not None:
        id_str = " id = \"%s\"" % id
    if style is not None:
        style_str = " style = \"%s\"" % style
    if style_cell is not None:
        style_cell_str = " style = \"%s\"" % style_cell
    if style_header is not None:
        style_header_str = " style = \"%s\"" % style_header
    else:
        style_header_str = style_cell_str
    s = "<table" + class_str + id_str + style_str + ">\n"

    # create row for header
    if len(header) > 0:
        s += "<tr>\n"
        for h in header:
            s += "<th" + style_header_str + ">" + str(h) + "</th>\n"
        s += "</tr>\n"

    # create entry for each row of content
    for row in content:
        s += "<tr>\n"

        for col in row:
            s += "<td" + style_cell_str + ">" + str(col) + "</td>\n"

        s += "</tr>\n"

    s += "</table>\n"

    return s