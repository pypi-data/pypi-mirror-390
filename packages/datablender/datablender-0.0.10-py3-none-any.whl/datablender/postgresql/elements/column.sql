with a as (

	select
		a.attname column_name,
		b.relname table_name,
		c.nspname schema_name,
		case d.typname
			when '_int4'
    		then 'int4[]'
			when 'geometry'
    		then concat(d.typname,'(',e."type",',',e.srid,')')
        	else d.typname
    	end "type",
    	a.attnotnull has_not_null_constraint,
		f.conname,
--		array_agg(distinct 
			h.relname
--		) "indexes"
			,
			b.*
	from pg_catalog.pg_attribute a 
	left join pg_catalog.pg_class b
		on a.attrelid = b."oid" 
	left join pg_catalog.pg_namespace c
		on b.relnamespace = c."oid"
	left join pg_catalog.pg_type d
		on a.atttypid = d."oid"
	left join geometry_columns AS e
		on c.nspname = e.f_table_schema
		and b.relname = e.f_table_name
		and a.attname = e.f_geometry_column
	left join pg_catalog.pg_constraint f
		on a.attrelid = f.conrelid
		and a.attnum = ANY (f.conkey) 
	left join pg_catalog.pg_index g
		on a.attrelid = g.indrelid
		and a.attnum = ANY (g.indkey)
	left join pg_catalog.pg_class h
		on g.indexrelid = h."oid"
	where a.attstattarget < 0
		and b.relkind = 'r'-- m materialized -- v view
	
	
)--, b as (
	select
		column_name "name",
		element_name,
		schema_name,
		"type",
		has_not_null_constraint,
		array_agg( 
			json_build_object(
				'name',conname,
				'type',contype
			)
		) filter(where conname is not null) "constraints"
	from a
	group by 1,2,3,4,5
	
)
select
	"name",
	element_name,
	schema_name,
	"type",
	has_not_null_constraint,
	case
		when TRUE = ANY (SELECT unnest("constraints") IS NULL)
		then null
		else array_to_json("constraints")
	end "constraints",
	case
		when TRUE = ANY (SELECT unnest("indexes") IS NULL)
		then null
		else array_to_json("indexes")
	end "indexes"
from a
order by 3 desc,2
;

select *
from pg_index

select relkind,count(*),array_agg(relname order by relname)
from pg_class
group by 1
order by 1

select *
from pg_namespace
