select
	b.relname "name",
	c.relname element_name,
	d.nspname schema_name,
	f.conname is not null is_constraint,
	case f.contype
		when 'u'
		then 'unique'
		when 'f'
		then 'foreign key'
		when 'p'
		then 'primary key'
		when 'c'
		then 'check'
	end constraint_type,
	array_to_json(array_agg(e.attname)) "columns"
from pg_index a
left join pg_catalog.pg_class b on a.indexrelid = b."oid" 
left join pg_catalog.pg_class c on a.indrelid  = c."oid" 
left join pg_catalog.pg_namespace d on b.relnamespace = d."oid" 
left join pg_catalog.pg_attribute e on e.attrelid = c."oid" and e.attnum = ANY (a.indkey)
left join pg_catalog.pg_constraint f on b.relname = f.conname and b.relnamespace = f.connamespace 
group by 1,2,3,4,5
;
