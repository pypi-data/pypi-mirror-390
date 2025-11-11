select
	action_name,
	action_time,
	jsonb_build_object(
		'element_type',action_element_type,
		'id',action_element_id,
		'name',action_element_name,
		'schema_name',action_element_schema_name
	) element,
	array_agg( 
		jsonb_build_object(
			'id',id,
			'name',"name",
			'element_type',element_type,
			'element_id',element_id,
			'element_name',element_name,
			'element_schema_name',element_schema_name,
			'time',event_time,
			'duration',duration,
			'informations',informations
		) 
	) events
from data_events 
group by
	1,
	2,
	action_element_type,
	action_element_id,
	action_element_name,
	action_element_schema_name