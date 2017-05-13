import sqlite3
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
import sys
import csv


reload(sys)
sys.setdefaultencoding('utf-8')

conn = sqlite3.connect("databases/nsf-awards.db")
conn.execute("CREATE TABLE IF NOT EXISTS Award(aid INT PRIMARY KEY, amount INT, title VARCHAR(250), year INT, startdate DATE, enddate DATE, dir VARCHAR(150), div VARCHAR(100))")
conn.execute("CREATE TABLE IF NOT EXISTS Institution(aid INT, instName VARCHAR(250), address VARCHAR(300), PRIMARY KEY (aid, instName))")
conn.execute("CREATE TABLE IF NOT EXISTS Investigator(aid INT, name VARCHAR(250), email VARCHAR(250), PRIMARY KEY (aid, name, email))")
conn.commit()

def exportDBToCSV():
    curs = conn.cursor()
    curs.execute("SELECT * FROM Award")
    with open('Award.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["aid","amount","title","year","startdate","enddate","dir","div"])
        writer.writerows(curs.fetchall())
    curs.execute("SELECT * FROM Institution")
    with open('Institution.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["aid", "instName", "address"])
        writer.writerows(curs.fetchall())
    curs.execute("SELECT * FROM Investigator")
    with open('Investigator.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["aid", "name", "email"])
        writer.writerows(curs.fetchall())
    curs.close()

def insertAwardsXML():
    onlyfiles = [join("datasets/awards/", f) for f in listdir("datasets/awards/") if isfile(join("datasets/awards/", f))]
    for f in onlyfiles:
        try:
            print(f)
            tree = ET.parse(f)
            award = tree.getroot().find("Award")
            aid = award.find("AwardID").text
            startDate = award.find("AwardEffectiveDate").text
            division = getAcroynm(award.find("Organization").find("Division").find("LongName").text)
            directorate = getAcroynm(award.find("Organization").find("Directorate").find("LongName").text)
            insertAward(aid, award.find("AwardAmount").text, award.find("AwardTitle").text, startDate[-4:], startDate, award.find("AwardExpirationDate").text, directorate, division)

            instit = award.find("Institution")

            try:
                address = instit.find("StreetAddress").text + ", " + instit.find("CityName").text + ", " + instit.find("CountryName").text
                insertInstitution(aid, instit.find("Name").text, address)
            except TypeError:
                print("Parse Error!")

            invest = award.find("Investigator")
            name = invest.find("FirstName").text + " " + invest.find("LastName").text
            insertInvestigator(aid, name, invest.find("EmailAddress").text)
        except ET.ParseError:
            print("Parse error!")

def insertAward(aid, amount, title, year, startdate, enddate, dir, div):
    query = "INSERT INTO Award(aid, amount, title, year, startdate, enddate, dir, div) VALUES (" + str(aid) + "," + str(amount) + ",\"" + str(title).replace('"',"'") + "\"," + str(year) + "," + str(startdate) + "," + str(enddate) + ",\"" + str(dir).replace('"',"'") + "\",\"" + str(div).replace('"',"'") + "\")"
    #print(query)
    conn.execute(query)
    conn.commit()


def insertInstitution(aid, instName, address):
    query = "INSERT INTO Institution(aid, instName, address) VALUES (" + str(aid) + ",\"" + str(instName) + "\",\"" + str(address) + "\")"
    #print(query)
    conn.execute(query)
    conn.commit()

def insertInvestigator(aid, name, email):
    query = "INSERT INTO Investigator(aid, name, email) VALUES (" + str(aid) + ",\"" + str(name) + "\",\"" + str(email) + "\")"
    #print(query)
    conn.execute(query)
    conn.commit()

# For the director and division attributes
# Prefix is ignored, and the first letter of each word is returned (except ands, ofs, for, Direct, Directorate, Div, Division)
def getAcroynm(label):
    if(label == None):
        return None
    words = label.split(" ")
    if(label.isupper()):
        return label
    acroynm = ""
    for w in words:
        if(w.upper() != "OF" and w.upper() != "AND" and w.upper() != "FOR" and w.upper() != "DIRECT" and w.upper() != "DIRECTORATE" and w.upper() != "DIV" and w.upper() != "DIVISION" and w[0].isalpha()):
            acroynm += w[0]

    if (acroynm == "E"):
        acroynm = "ENG"
    elif (acroynm == "P"):
        acroynm = "PHYS"
    elif(acroynm == "C"):
        acroynm = "CHEM"
    elif(acroynm == "G"):
        acroynm = "GEO"
    elif(acroynm == "B"):
        acroynm = "BD"  #Budget division

    return acroynm

insertAwardsXML()
exportDBToCSV()