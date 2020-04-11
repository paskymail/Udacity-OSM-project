import sqlite3
from sqlite3 import Error

import pandas as pd
from pprint import pprint
import re

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

def update_table_from_dataframe(conn, df, table):
    """ update a table from the dataform
    :param conn: Connection object
    :param df: dataform withe the info to update
    :return:
    """
    try:
        cursor=conn.cursor()
        # creating column list for insertion
        cols = ",".join([str(i) for i in df.columns.tolist()])
        # Insert DataFrame recrds one by one.
        for i,row in df.iterrows():
            sql = "REPLACE INTO " + table + " ("+cols+") VALUES "+str(tuple(row))+";"
            print(sql)
            cursor.execute(sql)
        # the connection is not autocommitted by default, so we must commit to save our changes
        conn.commit()
    
    except Error as e:
        print(e)

def update_name(name, mapping):
    # YOUR CODE HERE
    for k, v in mapping.items():
        if re.search(rf"{k}", name, re.IGNORECASE):
            name = name.replace(k,mapping[k])      
    return name

def update_tags(df, column, mapping):
    df2 = df
    dummy = "a"
    for i, row in df.iterrows():
        dummy = row[column]
        df2[column][i]= update_name(dummy, mapping)
    return df2

database = r"DBTest.db"

query_tag_keys = """
SELECT ind, key, value
FROM nodes_tags
where (key = "zip") or (key = "state");
"""
mapping_keys = { 
             "zip": "postcode",
             "state": "country", 
            }

query_tag_numbers = """
SELECT ind, key, value
FROM nodes_tags
where key = "housenumber" and type = "addr" and (value LIKE '%;%' or value LIKE '%acc%');
"""

mapping_housenumbers = { 
             ";": "-",
             " acc": "", 
            }


query_tag_phone = """
SELECT ind, key, value, type
FROM nodes_tags
where (key = "phone") and type = "regular";
"""

mapping_phone = { 
             "regular": "contact"
            }

query_tag_color = """
SELECT ind, key, value
FROM nodes_tags
where (key = "colour") and not value LIKE '%#%';
"""

mapping_color = { 
             "white": "#ffffff",
             "black": "#000000",
             "red": "#ff0000",
             "yellow": "#FFFF00",
             "blue": "#0000FF"
            }         






###########################################################################
#Implement the corrections
###########################################################################


# create a database connection
conn = create_connection(database)
 
    # Get the dataframes
if conn is not None:
    
    #perform a query 
    # result = perform_query(conn, query_tag_keys)
    tag_keys = pd.read_sql_query(query_tag_keys, conn)
    housenumbers = pd.read_sql_query(query_tag_numbers, conn)
    phone = pd.read_sql_query(query_tag_phone, conn)
    color = pd.read_sql_query(query_tag_color, conn)

else:
    print("Error! cannot create the database connection.")


Corrected_keys = update_tags(tag_keys, "key", mapping_keys)

Corrected_housenumbers = update_tags(housenumbers, "value", mapping_housenumbers)

Corrected_phone = update_tags(phone, "type", mapping_phone)

Corrected_color = update_tags(color, "value", mapping_color)

pprint(Corrected_keys)

update_table_from_dataframe(conn, Corrected_keys, "nodes_tags")

conn.close()