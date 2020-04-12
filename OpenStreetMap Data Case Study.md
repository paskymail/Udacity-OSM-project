# OpenStreetMap Data Case Study

## Map Area
Sevilla, Andalusia, Spain

- [https://www.openstreetmap.org/relation/342563](https://www.openstreetmap.org/relation/342563)

This map is of my hometown, so I’m more interested to see what database querying reveals.

## Files used
1. Data.py
   It is used to parse the Open Street Map XML and create the following 5 tables on csv
      1. nodes.csv: contains the node information 
      - id: primary key
      - user: user name of the creator
      - uid: user Id
      - version
      - lat: latitude
      - lon: longitude
      - timestamp
      - changeset
  
      2. nodes_tags.csv: contains the tags asociated to the aforementioned nodes
      - ind: primary key
      - id:foreign key to the node id
      - key:the catalogue of tag
      - value: 
      - type: type of tag
      - 
      1. ways.csv: contains the way information 
      - id: primary key
      - user: user name of the creator
      - uid: user Id
      - version
      - timestamp
      - changeset
  
      1. ways_tags.csv: contains the tags asociated to the aforementioned nodes
      - Ind: primary key
      - id:foreign key to the way id
      - key:the catalogue of tag
      - value: 
      - type: type of tag

      1. ways_nodes.csv: contains the tags asociated to the aforementioned nodes
      - id:foreign key to the way id
      - node_id: foreign key to the node id
      - position: position in the list of nodes belonging to the way

   The Ind primary keys on the tags are added in order to update only these rows in the database when changes are made

2. QSL data.py
   It is used to create the SQL database (named OSMSevilla.db) where the tables are a mirror of the aforementioned csv tables. 
   It is also used to perform queries and cast the results into pandas dataframes which allow easier further manipulation

3. OSM Queries.sql
   It is used to perform queries to OSMDB.db using sqlite.
   This queries are then used in OSM audit.py to select only the problematic data to be treated. only the problematic rows are treated to be corrected.

4. OSM audit.py
   It is used to perform changes to the OSMDB.db in order to correct the problems found. 
   1. It performs queries to the DB to select only the problematic rows (when possible) and imports them into dataframes
   2. This dataframes are transformed and corrected
   3. the corrected dataframes are then exported to the database for update

## Problems Encountered in the Map
The first encountered problem was handling Unicode strings as the Spanish alphabet uses several special characters which where not correctly handled when converted to UTF-8 by DictWriter. Fortunately Python 3's built-in csv module supports Unicode natively by selecting encoding='utf-8-sig' when opening the csv. It worked!

Once ready, I screened a small sample size area around my house (so I know all the places around) and I run it against the data.py file done during the lesson exercises obtaining the DBTest.db

Once I got an idea of the problems I could found, I created the OSMSeville.db from the complete map of Seville (87MB) using the data.py and SQL data.py files.

Note that in SQL data.py I added an index as primary key to the nodes_tags and ways_tags tables so I can perform the update of selected rows by index.

Once, my database was ready, I followed the steps below to systematically screen the values of the tags:

   1. First, I filtered the tags by address type, since it should be the most regular. Here below I list the problems per found per key:
      1. Country
         1. No issues, all values to "ES"
      2. State
         1. State key should be replaced by Country
      3. Province
         1. No issues, all values to "Sevilla"
      4. City
         1. Some values of Sevilla are not correctly written or are in another language
         2. Some values included neighborhoods as for example " Sevilla / Casco Antiguo / San Bartolomé but seems structured and easy to undstand
      5. Postcode
         1. No issues, all postal codes are consistent
      6. Zip
         1. Zip key should be replaced by Postalcode
      7. Street
         1. Some abbreviations are found, although rare.
      8. House number
         1. There are some numbers with access letter associated, finding 3 acc A and 3A
         2. Some contains a list in 2 different forms: "1;2;3;4;5" "and 1-2-3-4-5". 


   2. Then  I took a look to the rest of tags types. Here below I list the problems per found per key:
      1. Phone
         1. Some numbers do not have the "+34" prefix
         2. Some keys where of type contact and other type regular
      2. Color
         1. Some colors are in HEX (#D6B290) and others as a color noun.

### 1.2 and 1.6 Replace and consolidate tag keys
In the file audit.py I created the functions to update any chosen column in accordance with a given dictionary.

In this case we will remove some redundant tag keys and change them by more appropriate ones.

The query filters the results to only treat the desired keys ("zip" and "state")

```python 
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

query_tag_keys = """
SELECT ind, key, value
FROM nodes_tags
where (key = "zip") or (key = "state");
"""
mapping_keys = { 
             "zip": "postcode",
             "state": "country", 
            }

tag_keys = pd.read_sql_query(query_tag_keys, conn)

Corrected_keys = update_tags(tag_keys, "key", mapping_keys)
````

As can be seen, both update_tags and update_name functions can be used for any correction. Only the query and mapping changes.

Therefore, for the next corrections only the query and mapping will be given as the other functions are reused.

Finally the following function is used to update the database with the information contained in the corrected dataframe

```python
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
            print(sql)
            cursor.execute(sql)
            # the connection is not autocommitted by default, so we must commit to save our changes
            conn.commit()
    
    except Error as e:
        print(e)
```

In order to be able to update the database easily, I decided to perform two diferent queries: one on the nodes_tags table and the other on the ways_tags tables. 

Note that we can also perform any of the shown queries to the combined nodes_tags and ways_tags tables as they share the same columns.

This can be done by performing the a UNION subquery and then performing the desired query on the subquery. 

Thus we need only to replace

```sql
SELECT ind, key, value
FROM nodes_tags
where (key = "zip") or (key = "state");
```
by the following query including the UNION subquery

```sql
SELECT tags.ind, tags.key, tags.value 
FROM (SELECT * FROM nodes_tags UNION 
      SELECT * FROM ways_tags) as tags
where (tags.key = "zip") or (tags.key = "state");
```

From now on we will only include the query on nodes_tags for simplicity.


### 1.4 standardize Sevilla city
After screening of the city names, I created a dictionary of Sevilla misspelings to replace them by "Sevilla".

```sql
SELECT ind, key, value
FROM nodes_tags
where key = "city" and type = "addr" ;
```

```python 
Corrected_city = update_tags(city, "value", mapping_city)

mapping_city = { 
             "Sevila": "Sevilla",
             "Seville": "Sevilla",
             "Sevillla": "Sevilla",
             "41008": "Sevilla",
             "41010": "Sevilla"
            }   
```

### 1.7 remove street abbreviations
After screening of the street names, I created a dictionary of abbreviations to replace them by the full noun.

```sql
SELECT ind, key, value
FROM nodes_tags
where (key = "street") and type = "addr" ;
```

```python 
Corrected_street = update_tags(street, "value", mapping_street)

mapping_street = { 
             "C/": "Calle",
             "Av.": "Avenida",
             "AVDA.": "Avenida",
             "Ctra.": "Carretera",
             "CTRA.": "Carretera",
             "CRTA.": "Carretera",
             "CR": "Carretera"
            }  
```

### 1.8 standardize house numbers
The following changes are made:
   - remove the acc abbreviation
   - change ";" for "-" in the number list 

```sql
SELECT ind, key, value
FROM nodes_tags
WHERE key = "housenumber" and type = "addr" and (value LIKE '%;%' or value LIKE '%acc%');
```

```python 
Corrected_housenumbers = update_tags(housenumbers, "value", mapping_housenumbers)

mapping_housenumbers = { 
             ";": "-",
             " acc": "", 
            }

````
### 2.1 standardize phone numbers
In the file audit.py the following changes are made:
   - tag type is changed for phone numbers from regular to contact

```sql
SELECT ind, key, value, type
FROM nodes_tags
where (key = "phone") and type = "regular";

```python 
Corrected_phone = update_tags(phone, "type", mapping_phone)

mapping_phone = { 
             "regular": "contact"
            }

````

### 2.2 standardize colors
The follwoing changes are made:
   - the color values that are expresed in nouns are changed into HEX codification

```sql
SELECT ind, key, value
FROM nodes_tags
where (key = "colour") and not value LIKE '%#%';
```

```python 
Corrected_color = update_tags(color, "value", mapping_color)

mapping_color = { 
             "white": "#ffffff",
             "black": "#000000",
             "red": "#ff0000",
             "yellow": "#FFFF00",
             "blue": "#0000FF"
            } 
````


## Other checks performed

### Postal Codes

Once the "zip" key is changed to "postcode", all postcodes are checked for consistency 

```sql
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION
      SELECT * FROM ways_tags) tags
WHERE tags.key='postcode' and not value LIKE '%41%'
GROUP BY tags.value;
```

Only one postcode was found inconsistent, that should be removed

```sql
	#	value	count
   1	18360	1
```

### Cities inclueded

```sql
SELECT tags.value, tags.key, tags.type, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = "city" and not tags.value LIKE "%Sevilla%"
GROUP BY tags.value
ORDER BY count DESC;
```
These are the other cities included, which are correct since they limit with Seville:

```sql
#|value|key|type|count
1|Tomares|city|addr|27
2|Camas|city|addr|25
3|San|Juan|de|Aznalfarache|city|addr|16
4|Castilleja|de|la|Cuestacity|addr|11
5|Alcalá|de|Guadaíra|city|	addr|6
6|Mairena|del|Aljarafe|city|addr|5
7|Alcalá|de|Guadaira|city|addr|3
8|Coca|de|la|Piñeracity|addr|3
9|Dos|Hermanas|city|addr|3
10|Montequinto|city|addr|3
11|camas|city|addr|3
12|Gelves|city|addr|1     
```

# Data Overview and Additional Ideas
This section contains basic statistics about the dataset and some additional ideas about the data in context.

### File sizes
```
Seville map.osm ......... 87 MB
OSMSeville.db .......... 53 MB
nodes.csv ............. 29 MB
nodes_tags.csv ........ 4 MB
ways.csv .............. 3 MB
ways_tags.csv ......... 5 MB
ways_nodes.cv ......... 12 MB  
```  

### Number of nodes
```
SELECT COUNT(*) FROM nodes;
```
355969

### Number of ways
```
SELECT COUNT(*) FROM ways;
```
56897

### Number of unique users
```sql
SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT users, uid FROM nodes UNION ALL SELECT user, uid FROM ways) e;
```
1046

### Top 10 contributing users to nodes and ways
```sql
SELECT e.user, COUNT(e.uid) as count         
FROM (SELECT uid, user FROM nodes UNION ALL SELECT uid, user FROM ways) e
GROUP BY e.user
ORDER BY count DESC
LIMIT 10;
```

```sql
#	user	count
1	erlenmeyer	104084
2	Juan Pedro Ruiz	50931
3	BoomEngine	33827
4	cirdancarpintero	28737
5	nonopp	15810
6	avm	14962
7	nanino90	11968
8	Alberto Molina	11090
9	Ro5597	8529
10	AtomMapper	7619
```

### Top 10 contributing users to tags (both for nodes and ways)
```sql
SELECT total.user, count(total.ind) as count
FROM (select w.user, w.ind FROM (SELECT ways.user, ways_tags.ind
FROM ways_tags JOIN ways WHERE ways_tags.id = ways.id) as w UNION select n.user, n.ind FROM (SELECT nodes.user, nodes_tags.ind
FROM nodes_tags JOIN nodes WHERE nodes_tags.id = nodes.id) as n) as total
GROUP by total.user
Order by count DESC
Limit 10;
```
```sql
#	user	count
1	erlenmeyer	45023
2	Juan Pedro Ruiz	26770
3	nyuriks	19686
4	BoomEngine	13496
5	mapman44	10263
6	avm	10127
7	sanchi	6944
8	Ro5597	6395
9	CristinaDC	5687
10	AtomMapper	5480
```
 
### Number of users appearing only once (having 1 post)
```sql
sqlite> SELECT COUNT(*) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num<10)  u;
```
642

# Additional Ideas

## Contributor statistics and gamification suggestion 
The contributions of users seems incredibly skewed, possibly due to automated versus manual map editing (the word “bot” appears in some usernames). Here are some user percentage statistics:

- Top user contribution percentage (“jumbanho”) 52.92%
- Combined top 2 users' contribution (“jumbanho” and “woodpeck_fixbot”) 83.87%
- Combined Top 10 users contribution
94.3%
- Combined number of users making up only 1% of posts 287 (about 85% of all users)

Thinking about these user percentages, I’m reminded of “gamification” as a motivating force for contribution. In the context of the OpenStreetMap, if user data were more prominently displayed, perhaps others would take an initiative in submitting more edits to the map. And, if everyone sees that only a handful of power users are creating more than 90% a of given map, that might spur the creation of more efficient bots, especially if certain gamification elements were present, such as rewards, badges, or a leaderboard. 

## Additional Data Exploration

### Top 10 appearing amenities

```sql
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```sql
place_of_worship  580       
school            402       
restaurant        80        
grave_yard        75        
parking           63        
fast_food         51        
fire_station      48        
fuel              31        
bench             30        
library           28 
```

### Biggest religion (no surprise here)

```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='place_of_worship') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='religion'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 1;
```
`christian   571`

### Most popular cuisines

```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC;
```

```sql
american    9         
pizza       5         
steak_hous  4         
chinese     3         
japanese    3         
mexican     3         
thai        3         
italian     2         
sandwich    2         
barbecue    1
```

# Conclusion
 After this review of the data it’s obvious that the Charlotte area is incomplete, though I believe it has been well cleaned for the purposes of this exercise. It interests me to notice a fair amount of GPS data makes it into OpenStreetMap.org on account of users’ efforts, whether by scripting a map editing bot or otherwise. With a rough GPS data processor in place and working together with a more robust data processor similar to data.pyI think it would be possible to input a great amount of cleaned data to OpenStreetMap.org.