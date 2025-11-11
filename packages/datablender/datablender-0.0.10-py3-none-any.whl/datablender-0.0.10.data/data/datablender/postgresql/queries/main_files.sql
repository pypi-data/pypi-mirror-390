select
	coalesce(
		(main_files[1]-> 'name')::text,
		"name"
	) "name",
	coalesce(
		(main_files[1]-> 'directory_name')::text,
		"directory_name"
	) "directory_name",
	"schema",
	array_agg(
		json_build_object(
			'tables',"tables",
			'name',"name",
			'id', id
		)
	) files
from public.files
group by 1,2,3