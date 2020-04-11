import sqlite3
from sqlite3 import Error

import pandas as pd


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def perform_query(conn, query):
    """ perform a query and return a dataframe with the result
    :param conn: Connection object
    :param query: the query to consult
    :return: results"""

    df=pd.DataFrame()

    try:
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        df = pd.DataFrame(rows)
        
    except Error as e:
        print(e)
    
    return df

def create_table_from_csv(conn, csvfile, table_name, index_val):
    """ create a table from the csv
    :param conn: Connection object
    :param csvfile: a csv file
    :param csvfile: the table_name
    :return:
    """
    try:
        df = pd.read_csv(csvfile)
        df.to_sql(table_name, conn, if_exists='append', index= index_val, index_label="Ind")
    except Error as e:
        print(e)

database = r"OSMSeville.db"
 
sql_create_table_nodes = """ CREATE TABLE IF NOT EXISTS nodes

(
    Id INTEGER PRIMARY KEY,
    Lat REAL,
    Lon REAL,
    User TEXT,
    UID INTEGER,
    Version INTEGER,
    Changeset INTEGER,
    Timestamp DATETIME, 
); """

sql_create_table_nodes_tags = """ CREATE TABLE IF NOT EXISTS nodes_tags

(
    Ind INTEGER PRIMARY KEY,
    Id INTEGER,
    FOREIGN KEY (Id) REFERENCES node (Id),
    Key TEXT,
    Value TEXT,
    Type TEXT, 
); """

sql_create_table_ways = """ CREATE TABLE IF NOT EXISTS ways

(
    Id INTEGER PRIMARY KEY,
    User TEXT,
    UID INTEGER,
    Version INTEGER,
    Changeset INTEGER,
    Timestamp DATETIME, 
); """

sql_create_table_ways_tags = """ CREATE TABLE IF NOT EXISTS ways_tags

(
    Ind INTEGER PRIMARY KEY,
    Id INTEGER,
    FOREIGN KEY (Id) REFERENCES ways (Id),
    Key TEXT,
    Value TEXT,
    Type TEXT, 
); """

sql_create_table_ways_nodes = """ CREATE TABLE IF NOT EXISTS ways_nodes

(
    Id INTEGER,
    FOREIGN KEY (Id) REFERENCES ways (Id),
    Node_id INTEGER,
    FOREIGN KEY (Node_id) REFERENCES nodes (Id),
    Position INTEGER,  
);"""

query = """
SELECT count(id) 
FROM nodes
WHERE timestamp > "2013-05-19";
"""

# STEPS to populate the database


# create a database connection
conn = create_connection(database)
 
    # create tables
if conn is not None:
    # create node table
    create_table(conn, sql_create_table_nodes)

    #populate nodes table
    csvfile = "nodes.csv"
    create_table_from_csv(conn, csvfile, "nodes", False)

    # create nodes_tags table
    create_table(conn, sql_create_table_nodes_tags)

    #populate nodes_tags table
    csvfile = "nodes_tags.csv"
    create_table_from_csv(conn, csvfile, "nodes_tags", True)

    # create ways table
    create_table(conn, sql_create_table_ways)

    #populate ways table
    csvfile = "ways.csv"
    create_table_from_csv(conn, csvfile, "ways",False)

    # create ways_tags table
    create_table(conn, sql_create_table_ways_tags)

    #populate ways_tags table
    csvfile = "ways_tags.csv"
    create_table_from_csv(conn, csvfile, "ways_tags", True)

    # create ways_nodes table
    create_table(conn, sql_create_table_ways_nodes)

    #populate ways_nodes table
    csvfile = "ways_nodes.csv"
    create_table_from_csv(conn, csvfile, "ways_nodes", False)

    #perform a query 
    result = perform_query(conn, query)
    print(result)

else:
    print("Error! cannot create the database connection.")
