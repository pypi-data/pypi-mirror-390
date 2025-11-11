select
	a.datname "name",
	pg_catalog.pg_get_userbyid(datdba) "owner",
    array_agg( 
		jsonb_build_object( 
			'user_name',b.usename,
			'privilege',c.privilege
		)
	) grants
from
	pg_catalog.pg_database a,
	pg_catalog.pg_user b,
	(values ('create'), ('connect'), ('temporary')) c(privilege)
WHERE
	pg_catalog.has_database_privilege(
		b.usename,
		a.datname,
		c.privilege
	) 
group by 1,2
;
