with a as (
	select
		b.nspname schema_name,
		a.proname routine_name,
		case a.prokind
			when 'f'
			then 'function'
			when 'p'
			then 'procedure'
			when 'a'
			then 'aggregate_function'
			when 'w'
			then 'window_function'
		end routine_type,
		c.usename "owner",
		prorettype,
		unnest(a.proargnames) argument_name,
		unnest(a.proallargtypes) argument_type,
		unnest(a.proargmodes) argument_mode,
		*
	from pg_catalog.pg_proc a
	left join pg_catalog.pg_namespace b on a.pronamespace = b."oid" 
	left join pg_catalog.pg_user c on a.proowner = c.usesysid 
)
select *
from a
--left join pg_catalog.pg_type pt 
where routine_type = 'function' and schema_name = 'public'
;