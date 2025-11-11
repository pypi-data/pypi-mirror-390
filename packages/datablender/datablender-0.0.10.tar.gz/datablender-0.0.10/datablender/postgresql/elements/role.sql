select
  usename as "name",
  usesuper is_superuser,
  usecreatedb can_create_database
FROM pg_catalog.pg_user
;