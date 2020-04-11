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

SELECT ind, key, value
FROM nodes_tags
where ((key = "zip") or (key = "state")) and type = "addr"