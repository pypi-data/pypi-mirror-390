with t as (
	-- Tables et leurs schémas
	select
		d."oid" id,
		d.relname "name",
		d.relowner owner_id,
		e."oid" schema_id,
		e.nspname schema_name
	from pg_catalog.pg_class d
	left join pg_catalog.pg_namespace e
		on d.relnamespace = e."oid"
	where
		d.relkind in ('r','p')	
		and not relispartition 
), i as (
	-- Indexes
	select
		c.relname "name",
		i.indrelid table_id,
		i.indisunique is_unique,
		a.amname "method",
		h.contype constraint_type,
		unnest(i.indkey) column_position
	from pg_index i
	left join pg_catalog.pg_class c
		on c."oid" = i.indexrelid
	left join t
		on t.id = indrelid
	left join pg_catalog.pg_am a
		on c.relam = a."oid"
	left join pg_catalog.pg_constraint h
		on h.conname = c.relname
	where t.id is not null
), i_ as (
	select
		"name",
		table_id,
		is_unique,
		"method",
		constraint_type,
		array_agg(a.attname) "columns"
	from i
	left join pg_attribute a
		on i.table_id = a.attrelid
		and i.column_position = a.attnum
	group by 1,2,3,4,5
), i__ as (
	select
		table_id,
		array_agg(
			json_build_object(
				'name',"name",
				'is_unique',is_unique,
				'method',"method",
				'constraint_type',
				case constraint_type
					when 'u'
					then 'unique'
					when 'f'
					then 'foreign key'
					when 'p'
					then 'primary key'
					when 'c'
					then 'check'
				end,
				'columns',"columns"
			) 
		) "indexes"
	from i_
	group by 1
),c1 as (
	-- Contraintes
	select *, unnest(conkey) column_position
	from pg_constraint
), c1_ as (
	select
		c1.conrelid table_id,
		c1."oid" id,
		c1.conname "name",
		c1.contype "type",
		array_agg(a.attname order by column_position) "columns"
	from c1
	left join pg_attribute a
		on c1.conrelid = a.attrelid
		and c1.column_position = a.attnum
	group by 1,2,3,4
), c2 as (
	select
		c."oid" id,
		c.confrelid reference_table_id,
		t."name" reference_table_name,
		t.schema_name reference_schema_name,
		unnest(c.confkey) column_position
	from pg_constraint c
	left join t
		on c.confrelid = t.id 
	where c.contype = 'f'
), c2_ as (
	select
		c2.id,
		c2.reference_table_name,
		c2.reference_schema_name,
		array_agg(a.attname) reference_columns
	from c2
	left join pg_attribute a
		on c2.reference_table_id = a.attrelid
		and c2.column_position = a.attnum
	group by 1,2,3
), cs as (
	select
		c1_.table_id,
		array_agg( 
			jsonb_build_object(
				'name',c1_."name",
				'type',
				case c1_."type"
					when 'u'
					then 'unique'
					when 'f'
					then 'foreign key'
					when 'p'
					then 'primary key'
					when 'c'
					then 'check'
				end,
				'columns',c1_."columns",
				'reference_schema_name',c2_.reference_schema_name,
				'reference_table_name',c2_.reference_table_name,
				'reference_columns',c2_.reference_columns,
				'clause',h.check_clause
			)
		) "constraints"
	from c1_
	left join c2_
		on c1_.id = c2_.id
	left join information_schema.check_constraints h
		on h.constraint_name = c1_."name"
	group by 1
), g as (
	-- Grants
	select
		t.id,
		t.schema_name,
		t."name",
	    t.owner_id,
	    array_agg( 
			jsonb_build_object( 
				'user_name',b.usename,
				'privilege',c.privilege
			)
		) grants
	from
		t,
		pg_catalog.pg_user b,
		(values ('select'), ('insert'), ('update'), ('delete'), ('references')) c(privilege)
	where
		pg_catalog.has_table_privilege(
			b.usename,
			quote_ident(t.schema_name) || '.' || quote_ident(t."name"),
			c.privilege
		)
		and t.schema_name not in ('pg_catalog','pg_toast','information_schema')
	group by 1,2,3,4
), c as (
	-- Columns
	select
		a.attrelid table_id,
		attname "name",
		case 
			when substring(d.typname from 1 for 1) = '_'
			then concat(
				substring(
					d.typname from 2 for length(d.typname)-1
				),
				'[]'
			)
			when d.typname = 'int4'
    		then 'int'
			when d.typname = 'int8'
    		then 'bigint'
			when d.typname = 'geometry'
    		then concat(d.typname,'(',e."type",',',e.srid,')')
        	else d.typname
    	end "type",
  		pg_get_serial_sequence(
  			'"'|| t.schema_name||'"."'||t."name"||'"',
  			attname
  		) is not null serial,    	
    	a.attnotnull has_not_null_constraint,
    	a.attnum column_position,
	  	c.conname constraint_name,
	  	c.contype constraint_type,
	  	case
	  		when c.contype != 'p' and  d.typname != 'serial'
	  		then de.adbin 
	  	end default_value,
	  	i.description "comment"
	from pg_catalog.pg_attribute a 
	left join t
		on a.attrelid = t.id
	left join pg_catalog.pg_type d
		on a.atttypid = d."oid"
	left join geometry_columns AS e
		on t.schema_name = e.f_table_schema
		and t."name" = e.f_table_name
		and a.attname = e.f_geometry_column
	left join pg_catalog.pg_constraint c
		on c.conrelid = a.attrelid
		and a.attnum =any(c.conkey) 
	left join pg_catalog.pg_attrdef de
		on de.adrelid = a.attrelid
		and de.adnum = a.attnum
	left join pg_catalog.pg_description i
		on i.objoid  = t.id
		and i.objsubid = a.attnum
	where
		t.id is not null
		and a.attnum > 0
), c_ as (
	select
		table_id,
		"name",
		"type",
		serial,
		column_position,
		has_not_null_constraint,
		default_value,
		"comment",
		array_agg(
			jsonb_build_object(
				'name',constraint_name,
				'type',	case constraint_type
					when 'u'
					then 'unique'
					when 'f'
					then 'foreign key'
					when 'p'
					then 'primary key'
					when 'c'
					then 'check'
				end
			)
		) filter(where constraint_name is not null) "constraints"
	from c
	group by 1,2,3,4,5,6,7,8
), c__ as (
	select
		table_id,
		array_agg(
			jsonb_build_object(
				'name',"name",
				'type',"type",
				'serial',serial,
				'default_value',default_value,
				'constraints',
				case
					when has_not_null_constraint
					then array_append(
						"constraints",
						jsonb_build_object(
							'name',concat("name",'_not_null'),
							'type','not_null'
						)
					)
					else "constraints"
				end,
				'comment',"comment"
			) 
			order by column_position
		) "columns"
	from c_
	group by 1
)
select
	g.schema_name,
	g."name",
	p.usename "owner",
	pg_total_relation_size('"'|| g.schema_name||'"."'||g."name"||'"') "size",
	g.grants,
	coalesce(cs."constraints",array[]::jsonb[]) "constraints",
	coalesce(i__."indexes",array[]::json[]) "indexes",
	c__."columns"
from g
left join pg_catalog.pg_user p
	on p.usesysid = g.owner_id
left join cs
	on g.id = cs.table_id
left join i__
	on i__.table_id = g.id
left join c__
	on c__.table_id = g.id
;
	
	
