with t as (
	-- Tables et leurs schémas
	select
		d."oid" id,
		d.relname "name",
		d.relowner owner_id,
		e."oid" schema_id,
		e.nspname schema_name,
		d.relkind = 'm' is_materialized
	from pg_catalog.pg_class d
	left join pg_catalog.pg_namespace e
		on d.relnamespace = e."oid"
	where
		d.relkind in ('m','v')
), i as (
	-- Indexes
	select
		i.indrelid view_id,
		c.relname "name",
		i.indisunique is_unique,
		a.amname "method",
		unnest(i.indkey) column_position
	from pg_index i
	left join pg_catalog.pg_class c
		on c."oid" = i.indexrelid
	left join t
		on t.id = indrelid
	left join pg_catalog.pg_am a
		on c.relam = a."oid"
	where t.id is not null
), i_ as (
	select
		view_id,
		"name",
		is_unique,
		"method",
		array_agg(a.attname) "columns"
	from i
	left join pg_attribute a
		on i.view_id = a.attrelid
		and i.column_position = a.attnum
	group by 1,2,3,4
), i__ as (
	select
		view_id,
		array_agg(
			json_build_object(
				'name',"name",
				'is_unique',is_unique,
				'method',"method",
				'columns',"columns"
			) 
		) "indexes"
	from i_
	group by 1
), g as (
	-- Grants
	select
		t.id,
		t.schema_name,
		t."name",
	    t.owner_id,
	    t.is_materialized,
	    array_agg( 
			jsonb_build_object( 
				'user_name',b.usename,
				'privilege',c.privilege
			)
		) grants
	from
		t,
		pg_catalog.pg_user b,
		(values ('select')) c(privilege)
	where
		pg_catalog.has_table_privilege(
			b.usename,
			quote_ident(t.schema_name) || '.' || quote_ident(t."name"),
			c.privilege
		)
		and t.schema_name not in ('pg_catalog','pg_toast','information_schema')
	group by 1,2,3,4,5
), c as (
	-- Columns
	select
		a.attrelid view_id,
		attname "name",
		case d.typname
			when '_int4'
    		then 'int4[]'
			when 'int4'
    		then 'int'
			when 'geometry'
    		then concat(d.typname,'(',e."type",',',case e.srid when 0 then 4326 else e.srid end,')')
        	else d.typname
    	end "type",    	
    	a.attnum column_position
	from pg_catalog.pg_attribute a 
	left join t
		on a.attrelid = t.id
	left join pg_catalog.pg_type d
		on a.atttypid = d."oid"
	left join geometry_columns e
		on t.schema_name = e.f_table_schema
		and t."name" = e.f_table_name
		and a.attname = e.f_geometry_column 
	where
		t.id is not null
		and a.attnum > 0
), c_ as (
	select
		view_id,
		array_agg(
			jsonb_build_object(
				'name',"name",
				'type',"type"
			) 
			order by column_position
		) "columns"
	from c
	group by 1
)
select
	g.schema_name,
	g."name",
	p.usename "owner",
	g.is_materialized,
	pg_total_relation_size('"'|| g.schema_name||'"."'||g."name"||'"') "size",
	substr(
		pg_get_viewdef('"'|| g.schema_name||'"."'||g."name"||'"'),
		1,
		length(pg_get_viewdef('"'|| g.schema_name||'"."'||g."name"||'"')) - 1
	) "query",
	g.grants,
	coalesce(i__."indexes",array[]::json[]) "indexes",
	c_."columns",
	true is_database_saved
from g
left join pg_catalog.pg_user p
	on p.usesysid = g.owner_id
left join i__
	on i__.view_id = g.id
left join c_
	on c_.view_id = g.id
;
	
