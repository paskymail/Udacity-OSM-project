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
   It is used to perform queries to OSMDB.db using sqlite

4. OSM audit.py
   It is used to perform changes to the OSMDB.db in order to correct the problems found. 
   1. It performs queries to the DB and import them into dataframes
   2. This dataframes are transformed and corrected
   3. the corrected dataframes are then exported to the database for update

## Problems Encountered in the Map
The first encountered problem was handling Unicode strings as the Spanish alphabet uses several special characters which where not correctly handled when converted to UTF-8 by DictWriter. Fortunately Python 3's built-in csv module supports Unicode natively by selecting encoding='utf-8-sig' when opening the csv. It worked!

Once ready, I screened a small sample size area around my house (so I know all the places around) and I run it against the data.py file done during the lesson exercises. 

I followed the steps below to systematically screen the values of the tags

   1. First, I filtered the tags by address type, since it should be the most regular. Here below I list the problems per found per key:
      1. Country
         1. No issues, all values to "ES"
      2. State
         1. State key should be replaced by Country
      3. Province
         1. No issues, all values to "Sevilla"
      4. City
         1. Some values contained information from other keys, as for example "Sevilla (Spain)"
         2. Some values included neighborhoods as for example " Sevilla / Casco Antiguo / San Bartolomé
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
In the file audit.py I created a function called update_keys to update the following keys
   - zip --> postcode
   - state --> country

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

As can be seen, both update tags and update_name functions can be used for any correction and only the query and mapping changes.

Therefore, for the next corrections only the query and mapping will be given as the functions are reused.

### 1.8 standardize house numbers
In the file audit.py I created a function called update_tags to make the following changes:
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
   - tag type is changed for phone numbers from regular --> contact

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
In the file audit.py the following changes are made:
   - color values expresed are nous are changed into HEX

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


### Postal Codes


```sql
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='postcode'
GROUP BY tags.value
ORDER BY count DESC;
```

Here are the top ten results, beginning with the highest count:

```sql
value|count
28205|900
28208|388
28206|268
28202|204
28204|196
28216|174
28211|148
28203|120
28209|104
28207|86
```

 These results were taken before accounting for Tiger GPS zip codes residing in second­ level “k” tags. Considering the relatively few documents that included postal codes, of those, it appears that out of the top ten, seven aren’t even in Charlotte, as marked by a “#”. That struck me as surprisingly high to be a blatant error, and found that the number one postal code and all others starting with“297”lie in Rock Hill, SC. So, I performed another aggregation to verify a certain suspicion...
# Sort cities by count, descending

```sql
sqlite> SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key LIKE '%city'
GROUP BY tags.value
ORDER BY count DESC;
```

And, the results, edited for readability:

```sql
Rock Hill   111       
Pineville   27        
Charlotte   26        
York        24        
Matthews    10        
Concord     4         
3000        3         
10          2         
Lake Wylie  2         
1           1         
3           1         
43          1         
61          1         
Belmont, N  1         
Fort Mill,  1         
```

These results confirmed my suspicion that this metro extract would perhaps be more aptly named “Metrolina” or the “Charlotte Metropolitan Area” for its inclusion of surrounding cities in the sprawl. More importantly, three documents need to have their trailing state abbreviations stripped. So, these postal codes aren’t “incorrect,” but simply unexpected. However, one final case proved otherwise.
A single zip code stood out as clearly erroneous. Somehow, a “48009” got into the dataset. Let’s display part of its document for closer inspection (for our purposes, only the “address” and “pos” fields are relevant):

```sql
sqlite> SELECT *
FROM nodes 
WHERE id IN (SELECT DISTINCT(id) FROM nodes_tags WHERE key='postcode' AND value='48009')
```
`1234706337|35.2134608|-80.8270161|movercash|433196|1|7784874|2011-04-06T13:16:06Z`

`sqlite> SELECT * FROM nodes_tags WHERE id=1234706337 and type='addr';`

```sql
1234706337|housenumber|280|addr
1234706337|postcode|48009|addr
1234706337|street|North Old Woodward Avenue|addr
```

 It turns out, *“280 North Old Woodward Avenue, 48009”* is in Birmingham, Michigan. All data in this document, including those not shown here, are internally consistent and verifiable, except for the latitude and longitude. These coordinates are indeed in Charlotte, NC. I’m not sure about the source of the error, but we can guess it was most likely sitting in front of a computer before this data entered the map. The document can be removed from the database easily enough.

# Data Overview and Additional Ideas
This section contains basic statistics about the dataset, the MongoDB queries used to gather them, and some additional ideas about the data in context.

### File sizes
```
charlotte.osm ......... 294 MB
charlotte.db .......... 129 MB
nodes.csv ............. 144 MB
nodes_tags.csv ........ 0.64 MB
ways.csv .............. 4.7 MB
ways_tags.csv ......... 20 MB
ways_nodes.cv ......... 35 MB  
```  

### Number of nodes
```
sqlite> SELECT COUNT(*) FROM nodes;
```
1471350

### Number of ways
```
sqlite> SELECT COUNT(*) FROM ways;
```
84502

### Number of unique users
```sql
sqlite> SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
337

### Top 10 contributing users
```sql
sqlite> SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```

```sql
jumbanho    823324    
woodpeck_f  481549    
TIGERcnl    44981     
bot-mode    32033     
rickmastfa  18875     
Lightning   16924     
grossing    15424     
gopanthers  14988     
KristenK    11023     
Lambertus   8066 
```
 
### Number of users appearing only once (having 1 post)
```sql
sqlite> SELECT COUNT(*) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num=1)  u;
```
56

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