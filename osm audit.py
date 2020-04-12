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
    :param table: table to be updated
    :return:
    """
    try:
        cursor=conn.cursor()
        # creating column list for insertion
        cols = ",".join([str(i) for i in df.columns.tolist()])
        # Insert DataFrame recrds one by one.
        for i,row in df.iterrows():
            sql = "REPLACE INTO " + table + " ("+cols+") VALUES "+str(tuple(row))+";"
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

database = r"OSMSeville.db"

query_tag_keys = """
SELECT ind, key, value
FROM nodes_tags
where (key = "zip") or (key = "state");
"""
mapping_keys = { 
             "zip": "postcode",
             "state": "country",
             "flats": "housenumber" 
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

query_tag_street = """
SELECT ind, key, value
FROM nodes_tags
where (key = "street") and type = "addr" ;
"""

mapping_street = { 
             "C/": "Calle",
             "Av.": "Avenida",
             "AVDA.": "Avenida",
             "Ctra.": "Carretera",
             "CTRA.": "Carretera",
             "CRTA.": "Carretera",
             "CR": "Carretera"
            }    

query_tag_city = """
SELECT ind, key, value
FROM nodes_tags
where key = "city" and type = "addr" ;
"""

mapping_city = { 
             "Sevila": "Sevilla",
             "Seville": "Sevilla",
             "Sevillla": "Sevilla",
             "41008": "Sevilla",
             "41010": "Sevilla"
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
    street = pd.read_sql_query(query_tag_street, conn)
    city = pd.read_sql_query(query_tag_city, conn)

else:
    print("Error! cannot create the database connection.")


Corrected_keys = update_tags(tag_keys, "key", mapping_keys)

Corrected_housenumbers = update_tags(housenumbers, "value", mapping_housenumbers)

Corrected_phone = update_tags(phone, "type", mapping_phone)

Corrected_color = update_tags(color, "value", mapping_color)

Corrected_street = update_tags(street, "value", mapping_street)

Corrected_city = update_tags(city, "value", mapping_city)

pprint(Corrected_city)

##############################################################
#Update the database

#update_table_from_dataframe(conn, Corrected_city, "nodes_tags")

#################################################################

conn.close()