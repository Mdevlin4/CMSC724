import sqlite3
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

conn = sqlite3.connect("databases/nsf-awards.db")
conn.execute("CREATE TABLE IF NOT EXISTS Award(aid INT PRIMARY KEY, amount INT, title VARCHAR(250), year INT, startdate DATE, enddate DATE, dir VARCHAR(150), div VARCHAR(100))")
conn.execute("CREATE TABLE IF NOT EXISTS Institution(aid INT, instName VARCHAR(250), address VARCHAR(300), PRIMARY KEY (aid, instName))")
conn.execute("CREATE TABLE IF NOT EXISTS Investigator(aid INT, name VARCHAR(250), email VARCHAR(250), PRIMARY KEY (aid, name, email))")
conn.commit()

def insertAwardsXML():
    onlyfiles = [join("datasets/awards/", f) for f in listdir("datasets/awards/") if isfile(join("datasets/awards/", f))]
    for f in onlyfiles:
        try:
            print(f)
            tree = ET.parse(f)
            award = tree.getroot().find("Award")
            aid = award.find("AwardID").text
            startDate = award.find("AwardEffectiveDate").text
            division = award.find("Organization").find("Division").find("LongName").text
            directorate = award.find("Organization").find("Directorate").find("LongName").text
            insertAward(aid, award.find("AwardAmount").text, award.find("AwardTitle").text, startDate[-4:], startDate, award.find("AwardExpirationDate").text, division, directorate)

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

insertAwardsXML()