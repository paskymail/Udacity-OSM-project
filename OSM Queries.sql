-- SELECT user, timestamp 
-- FROM nodes
-- WHERE user = "erlenmeyer" and timestamp > "2016-01-01";

-- SELECT nodes.user, nodes.lat, nodes.lon, nodes_tags.value 
-- FROM nodes, nodes_tags
-- WHERE nodes.id = nodes_tags.id and user = "erlenmeyer" and timestamp > "2016-01-01"
-- LIMIT 5;

-- SELECT ways.user, ways_tags.value 
-- FROM ways, ways_tags
-- WHERE ways.id = ways_tags.id and user = "erlenmeyer" and timestamp > "2016-01-01"
-- LIMIT 5;

-- SELECT id, max(position) as suma
-- FROM ways_nodes
-- GROUP By id
-- Order by suma DESC;

-- SELECT ways_tags.value, nodes.user, max(ways_nodes.position) 
-- FROM nodes, ways_nodes, ways, ways_tags
-- WHERE ways_nodes.id = ways.id and ways.id = ways_tags.id and nodes.id = ways_nodes.node_id and nodes.user = "erlenmeyer" and nodes.timestamp > "2016-01-01"
-- GROUP BY ways_tags.value
-- LIMIT 5;

-- SELECT ind, key, value
-- FROM nodes_tags
-- where ((key = "zip") or (key = "state")) and type = "addr"
-- UNION
-- SELECT ind, key, value
-- FROM  ways_tags
-- where ((key = "zip") or (key = "state")) and type = "addr";


-- SELECT ind, key, value
-- FROM nodes_tags
-- where key = "housenumber" and type = "addr" and (value LIKE '%;%' or value LIKE '%acc%');

-- SELECT ind, key, value, type
-- FROM nodes_tags
-- where (key = "phone") and type = "regular";

-- SELECT ind, key, value
-- FROM nodes_tags
-- where (key = "colour") and not value LIKE '%#%';

-- SELECT ind, key, value
-- FROM nodes_tags
-- where ((key = "zip") or (key = "state")) and type = "addr"

-- SELECT ind, key, value
-- FROM nodes_tags
-- where (key = "street") and type = "addr" ;

-- SELECT tags.value, COUNT(*) as count 
-- FROM (SELECT * FROM nodes_tags 
-- 	  UNION
--       SELECT * FROM ways_tags) tags
-- WHERE tags.key='postcode' and not value LIKE '%41%'
-- GROUP BY tags.value
-- ORDER BY count DESC;


-- SELECT tags.value, tags.key, tags.type, COUNT(*) as count 
-- FROM (SELECT * FROM nodes_tags UNION ALL 
--       SELECT * FROM ways_tags) tags
-- WHERE tags.key = "city" and not tags.value LIKE "%Sevilla%"
-- GROUP BY tags.value
-- ORDER BY count DESC;

-- SELECT COUNT(*) FROM nodes;

-- SELECT COUNT(*) FROM ways;


-- SELECT e.user, COUNT(e.uid) as count         
-- FROM (SELECT uid, user FROM nodes UNION ALL SELECT uid, user FROM ways) e
-- GROUP BY e.user
-- ORDER BY count DESC
-- LIMIT 10;

-- SELECT e.user, COUNT(e.uid) as count         
-- FROM (SELECT uid, user FROM nodes UNION ALL SELECT uid, user FROM ways) e
-- GROUP BY e.user;

-- SELECT nodes.user, count(nodes_tags.ind) as count
-- FROM nodes_tags JOIN nodes
-- WHERE nodes_tags.id = nodes.id
-- GROUP by user
-- Order by count DESC
-- Limit 10;

-- SELECT ways.user, count(ways_tags.ind) as count
-- FROM ways_tags JOIN ways
-- WHERE ways_tags.id = ways.id
-- GROUP by user
-- Order by count DESC
-- Limit 10;

-- SELECT total.user, count(total.ind) as count
-- FROM (select w.user, w.ind FROM (SELECT ways.user, ways_tags.ind
-- FROM ways_tags JOIN ways WHERE ways_tags.id = ways.id) as w UNION select n.user, n.ind FROM (SELECT nodes.user, nodes_tags.ind
-- FROM nodes_tags JOIN nodes WHERE nodes_tags.id = nodes.id) as n) as total
-- GROUP by total.user
-- Order by count DESC
-- Limit 10;

-- SELECT COUNT(*) 
-- FROM
--     (SELECT e.user, COUNT(*) as num
--      FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
--      GROUP BY e.user
--      HAVING num<10)  u;

-- SELECT value, COUNT(*) as num
-- FROM nodes_tags
-- WHERE key='amenity'
-- GROUP BY value
-- ORDER BY num DESC
-- LIMIT 10;

-- SELECT tags.key, tags.type, COUNT(*) as num
-- FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) tags
-- WHERE not tags.type = "addr"
-- GROUP BY tags.key
-- ORDER BY num DESC
-- LIMIT 10;

-- SELECT tags.key, tags.type, tags.value, COUNT(*) as num
-- FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) tags
-- WHERE not tags.type = "addr" and (tags.key ="highway" or tags.key ="oneway")
-- GROUP BY tags.value
-- ORDER BY num DESC
-- LIMIT 5;


-- SELECT tags.key, tags.value, COUNT(*) as num
-- FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) tags
-- WHERE  tags.key ="amenity"
-- GROUP BY tags.value
-- ORDER BY num DESC
-- LIMIT 5;

-- SELECT nodes_tags.value, COUNT(*) as num
-- FROM nodes_tags JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
-- WHERE nodes_tags.id=i.id and nodes_tags.key='cuisine'
-- GROUP BY nodes_tags.value
-- ORDER BY num DESC
-- LIMIT 5;

-- SELECT nodes_tags.value, COUNT(nodes_tags.value) as num
-- FROM nodes_tags JOIN nodes
-- WHERE nodes_tags.id=nodes.id and nodes_tags.key='cuisine'
-- GROUP BY nodes_tags.value
-- ORDER BY num DESC
-- LIMIT 5;

-- SELECT COUNT(nodes_tags.value) as num
-- FROM nodes_tags JOIN nodes
-- WHERE nodes_tags.id=nodes.id and nodes_tags.key='cuisine' and (nodes_tags.value LIKE "%spanish%" or nodes_tags.value LIKE "%local%" or nodes_tags.value LIKE "%regional%" or nodes_tags.value LIKE "%tapas%");

-- SELECT COUNT(nodes_tags.value) as num
-- FROM nodes_tags JOIN nodes
-- WHERE nodes_tags.id=nodes.id and nodes_tags.key='cuisine';

SELECT key, type, value, COUNT(*) as num
FROM nodes_tags
WHERE not type = "addr" and key ="natural"
GROUP BY value
ORDER BY num DESC
LIMIT 5;