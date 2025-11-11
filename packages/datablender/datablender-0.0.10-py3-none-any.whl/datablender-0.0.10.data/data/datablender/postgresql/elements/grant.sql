select
	null schema_name,
	a.nspname element_name,
	'schema' element_type,
	b.usename user_name,
	c.privilege,
	pg_catalog.has_schema_privilege(b.usename, a.nspname, c.privilege) has_privilege
from
	pg_catalog.pg_namespace a,
	pg_catalog.pg_user b,
	(values ('create'), ('usage')) c(privilege)
union
select
	a.schemaname schema_name,
	a.tablename element_name,
	'table' element_type,
	b.usename user_name,
	c.privilege,
	pg_catalog.has_table_privilege(
		b.usename,
		quote_ident(a.schemaname) || '.' || quote_ident(a.tablename),
		c.privilege
	) has_privilege
from
	pg_catalog.pg_tables a,
	pg_catalog.pg_user b,
	(values ('select'), ('insert'), ('update'), ('delete'), ('references')) c(privilege)
union
select
	null schema_name,
	a.datname element_name,
	'database' element_type,
	b.usename user_name,
	c.privilege,
	pg_catalog.has_database_privilege(
		b.usename,
		a.datname,
		c.privilege
	) has_privilege
from
	pg_catalog.pg_database a,
	pg_catalog.pg_user b,
	(values ('create'), ('connect'), ('temporary')) c(privilege)
;