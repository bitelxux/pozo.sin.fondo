import MySQLdb

#db = MySQLdb.connect("localhost","root","eliquela","mysql_alexa" )
# It doesn't work with localhost
db = MySQLdb.connect("127.0.0.1","root","changeme", "mysql")
cursor = db.cursor()
cursor.execute("create database IF NOT EXISTS alexa")
cursor.execute("use alexa")

table_def = """
CREATE TABLE IF NOT EXISTS memories (
   id MEDIUMINT NOT NULL AUTO_INCREMENT,
   datetime datetime,
   user_id CHAR(255) NOT NULL,
   what VARCHAR(512) NOT NULL,
   PRIMARY KEY (id)
   );
"""

cursor.execute(table_def)


table_def = """
CREATE TABLE IF NOT EXISTS persons (
   id varchar(32),
   name varchar(32),
   PRIMARY KEY (id)
   );
"""
cursor.execute(table_def)

table_def = """
CREATE TABLE IF NOT EXISTS users (
   id varchar(32),
   name varchar(32),
   PRIMARY KEY (id)
   );
"""
cursor.execute(table_def)

db.commit()
db.close()

