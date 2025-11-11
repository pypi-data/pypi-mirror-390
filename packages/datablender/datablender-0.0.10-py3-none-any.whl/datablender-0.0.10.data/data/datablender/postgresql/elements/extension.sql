select
	extname "name",
	pg_catalog.pg_get_userbyid(extowner) as "owner"
FROM pg_extension
where extname != 'plpgsql'
;