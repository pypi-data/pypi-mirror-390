select
	pid,
	usename,
	backend_start,
	state,
	query
FROM pg_stat_activity
--WHERE state = 'active'-- and pid = 1119479
order by 2,3
;


SELECT 
   pg_terminate_backend(24668)
   
   pg_terminate_backend(12000),
   pg_terminate_backend(14416),
   pg_terminate_backend(12936)
   
   pg_terminate_backend(19948),
   pg_terminate_backend(3228)
--   --  *,
--   --  pid
--FROM 
--    pg_stat_activity 
--WHERE 
--    -- don't kill my own connection!
--    pid <> pg_backend_pid()
--    -- don't kill the connections to other databases
--    --AND datname = 'dobby'
--    and usename = 'jdouville'
--    ;
