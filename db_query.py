import sqlite3
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

#query = "SELECT B.instName, SUM(A.amount) AS totalAward FROM Award A, Institution B WHERE A.aid = B.aid AND dir = 'CS' AND year >= 1990 GROUP BY B.instName ORDER BY totalAward DESC LIMIT 5"
query = "SELECT * FROM Award WHERE dir LIKE '%Computer%' LIMIT 25"
conn = sqlite3.connect("databases/nsf-awards.db")
curs = conn.cursor()
curs.execute(query)
print(curs.fetchall())
curs.close()