"""
A PostgreSQL query for getting information about movies for loading
into the Elasticsearch index 'movies'.

The query retrieves only the information that has been modified AFTER
the previous loading to Elasticsearch.
"""
EXTRACT_QUERY = """
SELECT jsonb_build_object(
   'id', fw.id,
   'title',fw.title,
   'description',fw.description,
   'imdb_rating',fw.rating,
   'type',fw.type,
   'people', COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'role', pfw.role,
               'id', p.id,
               'name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ),
   'genre', array_agg(DISTINCT g.name))
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > %s OR
g.modified > %s OR
p.modified > %s
GROUP BY fw.id
ORDER BY fw.modified;
"""
