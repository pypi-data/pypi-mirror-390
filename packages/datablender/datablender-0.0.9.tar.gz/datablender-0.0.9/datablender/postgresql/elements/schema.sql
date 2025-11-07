with a as (
	select
		schemaname "name",
		pg_total_relation_size('"'||schemaname||'"."'||tablename||'"') "size"
	from pg_catalog.pg_tables
	union
	select
		schemaname "name",
    	pg_total_relation_size('"'||schemaname||'"."'||matviewname||'"') "size"
	from pg_matviews
), b as (
	select
		a.nspname,
		array_agg( 
			jsonb_build_object( 
				'user_name',b.usename,
				'privilege',c.privilege
			)
		) grants
	from
		pg_catalog.pg_namespace a,
		pg_catalog.pg_user b,
		(values ('create'), ('usage')) c(privilege)
	where 
		pg_catalog.has_schema_privilege(b.usename, a.nspname, c.privilege)
	group by 1
), c as (
	select
		b.schema_name "name",
		b.schema_owner "owner",
	    coalesce(sum(a."size"),0) "size"
	from a
	full join information_schema.schemata b on a."name" = b.schema_name
	where b.schema_name not in ('pg_catalog','pg_toast','information_schema')
	group by 1,2
)
select	
	c.*,
	b.grants
from c
left join b
	on c."name" = b.nspname
;


