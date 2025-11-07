select
	a.conname "name",
	case a.contype
		when 'u'
		then 'unique'
		when 'f'
		then 'foreign key'
		when 'p'
		then 'primary key'
		when 'c'
		then 'check'
	end "type",
	b.relname table_name,
	c.nspname schema_name,
	case
		when b.relname is null
		then null
		else array_to_json(array_agg(f.attname))
	end "columns",
	h.check_clause clause,
	d.relname reference_table_name,
	e.nspname reference_schema_name,
	case
		when d.relname is null
		then null
		else array_to_json(array_agg(g.attname))
	end reference_columns
from pg_constraint a
left join pg_catalog.pg_class b on a.conrelid = b."oid" 
left join pg_catalog.pg_namespace c on a.connamespace = c."oid" 
left join pg_catalog.pg_class d on a.confrelid = d."oid" 
left join pg_catalog.pg_namespace e on d.relnamespace = e."oid"
left join pg_catalog.pg_attribute f
	on f.attrelid = b."oid"
	and f.attnum = ANY (a.conkey)
left join pg_catalog.pg_attribute g
	on g.attrelid = d."oid"
	and g.attnum = ANY (a.confkey) 
left join information_schema.check_constraints h on h.constraint_name = a.conname
group by 1,2,3,4,6,7,8
;



