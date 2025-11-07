with p as (
	select
		partrelid table_id,
		case p.partstrat 
			when 'h' then 'hash'
			when 'l' then 'list'
			when 'r' then 'range'
		end "method",
		unnest(p.partattrs) column_index
	from pg_catalog.pg_partitioned_table p	
), a as (
	select
		table_id,
		"method",
		array_agg(a.attname) column_names
	from p
	left join pg_catalog.pg_attribute a
		on p.table_id = a.attrelid 
		and p.column_index = a.attnum
	group by 1,2	
), c as (
	select
		c."oid" table_id,
		c.relname table_name,
		c.relnamespace schema_id,
		array_agg(
			jsonb_build_object(
				'name',d.relname,
				'expression',lower(pg_get_expr(d.relpartbound,d."oid"))
			) 
		) partitions
	from pg_catalog.pg_class d
	left join pg_catalog.pg_inherits i
		on d."oid" = i.inhrelid
	left join pg_catalog.pg_class c
		on c."oid" = i.inhparent 
	where
		d.relkind in ('r','p')	
		and d.relispartition 
	group by 1,2
)
select
	c.table_name,
	e.nspname schema_name,
	c.partitions,
	a."method",
	a.column_names
from c
left join pg_catalog.pg_namespace e
	on c.schema_id = e."oid"
left join a
	on c.table_id = a.table_id


	