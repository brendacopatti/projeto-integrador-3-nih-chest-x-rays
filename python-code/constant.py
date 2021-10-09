#POSTGRESQL CONNECTION
POSTGRESQL_HOST='localhost'
POSTGRESQL_DATABASE='nih-chest-x-rays'
POSTGRESQL_USER='utfpr'
POSTGRESQL_PASSWORD='senhautfpr'

#DROP TABLES
SQL_DROP_X_RAY='drop table if exists x_ray'
SQL_DROP_FOLLOW_UP='drop table if exists follow_up'
SQL_DROP_PATIENT='drop table if exists patient'

#CREATE TABLES
SQL_CREATE_PATIENT='create table if not exists patient(id integer not null, gender char(1), constraint pk_patient primary key (id));'
SQL_CREATE_FOLLOW_UP='create table if not exists follow_up(id integer not null,	patient_id integer not null, patient_age smallint, patient_age_group VARCHAR(20), finding_label varchar(70),constraint pk_follow_up primary key (id, patient_id),constraint fk_patient foreign key (patient_id) references patient(id));'
SQL_CREATE_X_RAY='create table if not exists x_ray(follow_up_id integer not null, patient_id integer not null, view_position char(2), image bytea, original_image_width decimal(7,2),	original_image_height decimal(7,2),	original_image_pixels decimal(10,8), histogram float[256], constraint pk_x_ray primary key (follow_up_id, patient_id), constraint fk_follow_up foreign key (follow_up_id, patient_id) references follow_up(id, patient_id));'

#INSERT DATA
SQL_INSERT_PATIENT='insert into patient(id, gender) values (%s, %s);'
SQL_INSERT_FOLLOW_UP='insert into follow_up(id, patient_id, patient_age, patient_age_group, finding_label) values (%s, %s, %s, %s, %s);'
SQL_INSERT_X_RAY='insert into x_ray(follow_up_id, patient_id, view_position, image, original_image_width, original_image_height, original_image_pixels, histogram) values (%s, %s, %s, bytea(%s), %s, %s, %s, %s)'

#PROJECT
PROJECT_DIRECTORY='/home/luizim/Documentos/UTFPR/Dev/projeto-integrador-3-radiografia-torax'
DATA_DIRECTORY='/data'
IMAGES_001_DIRECTORY='/images_001'
IMAGES_002_DIRECTORY='/images_002'
DATA_ENTRY_CSV_FILE='/Data_Entry_2017.csv'

#COLUMS DATAFRAME
IMAGE_FILE_NAME='image_file_name'
FINDING_LABEL='finding_label'
FOLLOW_UP_ID='follow_up_id'
PATIENT_ID='patient_id'
PATIENT_AGE='patient_age'
PATIENT_GENDER='patient_gender'
VIEW_POSITION='view_position'
ORIGINAL_IMAGE_WIDTH='original_image_width',
ORIGINAL_IMAGE_HEIGHT='original_image_height',
ORIGINAL_IMAGE_SPACING='original_image_pixel_spacing'
IMAGE_DIRECTORY_FILE_NAME='image_directory_file_name'
PATIENT_AGE_GROUP='patient_age_group'

#AGE GROUPS
BABIES='Babies'
CHILDREN='Children'
YOUNG_ADULTS='Young adults'
MIDDLE_AGED_ADULTS='Middle-aged adults'
OLD_ADULTS='Old adults'

#NEW FUNCTIONS
L1 = '''
create or replace function l1(elem1 float[], elem2 float[]) returns float as $$
declare
 size integer;
 somat float;
begin
 select cardinality(histogram) into size from continous limit 1;
 somat := 0;
 for i in 1..size loop
    somat := somat + ABS(elem1[i] - elem2[i]);
 end loop;
 return somat;
end $$
language plpgsql;
'''
L2 = '''
create or replace function l2(elem1 float[], elem2 float[]) returns float as $$
declare
 size integer;
 somat float;
begin
 select cardinality(histogram) into size from continous limit 1;
 somat := 0;
 for i in 1..size loop
    somat := somat + (ABS(elem1[i] - elem2[i])*ABS(elem1[i] - elem2[i]));
 end loop;
 return sqrt(somat);
end $$
language plpgsql; 
'''
COSINE='''
create or replace function cosine(elem1 float[], elem2 float[]) returns float as $$
declare
 size integer;
 dotprod float;
 norm_a float;
 norm_b float;
begin
 select cardinality(histogram) into size from x_ray limit 1;
 dotprod := 0;
 norm_a := 0;
 norm_b := 0;
 for i in 1..size loop
    dotprod := dotprod + (elem1[i] * elem2[i]);
	norm_a := norm_a + (elem1[i] * elem1[i]);
	norm_b := norm_b + (elem2[i] * elem2[i]);
 end loop;
 return (dotprod) / (sqrt(norm_a) * sqrt(norm_b));
end $$
language plpgsql;
'''
GETHIST = '''
create or replace function get_features(flw_id integer, pat_id integer)
returns float[] as $$
declare
  out_vec float[];
begin
  select xr.histogram
    into out_vec
	from x_ray xr
	where xr.patient_id = pat_id and follow_up_id = flw_id;
	
	return out_vec;
end; $$ language plpgsql;
'''
RQueryL1 = '''
create or replace function RangeQueryl1(
	flw_id integer,
	pat_id integer,
	radius float
) 
returns table (
	follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query
      select xr.follow_up_id,
			 xr.patient_id,
			 l1(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      where l1(get_features(flw_id, pat_id), xr.histogram) <= radius;
end $$
language plpgsql;
'''

RQueryL2 = '''
create or replace function RangeQueryl2(
	flw_id integer,
	pat_id integer,
	radius float
) 
returns table (
	follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query
      select xr.follow_up_id,
			 xr.patient_id,
			 l1(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      where l2(get_features(flw_id, pat_id), xr.histogram) <= radius;
end $$
language plpgsql;
'''

RQueryCos = '''
create or replace function RangeQueryCos(
	flw_id integer,
	pat_id integer,
	radius float
) 
returns table (
	follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query
      select xr.follow_up_id,
			 xr.patient_id,
			 cosine(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      where cosine(get_features(flw_id, pat_id), xr.histogram) >= radius;
end $$
language plpgsql;
'''

KNNL1 ='''
create or replace function KNNl1(
    	flw_id integer,
        pat_id integer,
        k integer
        ) 
returns table (	
    follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query 
            select xr.follow_up_id,
			 xr.patient_id,
             l1(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      order by l1(get_features(flw_id, pat_id), xr.histogram) LIMIT k;
 end $$
 language plpgsql;
 '''
 
 
KNNL2 ='''
create or replace function KNNl2(
    	flw_id integer,
        pat_id integer,
        k integer
        ) 
returns table (	
    follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query 
            select xr.follow_up_id,
			 xr.patient_id,
             l2(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      order by l2(get_features(flw_id, pat_id), xr.histogram) LIMIT k;
 end $$
 language plpgsql;
 '''
 
KNNCOS = '''
create or replace function KNNcos(
    	flw_id integer,
        pat_id integer,
        k integer
        ) 
returns table (	
    follow_up_id integer,
	patient_id integer,
	distance float
) as $$
begin
  return query 
            select xr.follow_up_id,
			 xr.patient_id,
             cosine(get_features(flw_id, pat_id),
			    xr.histogram) as distance
      from x_ray xr
      order by cosine(get_features(flw_id, pat_id), xr.histogram) DESC 
	  LIMIT k;
 end $$
 language plpgsql;
 '''
 
FUNC_LIST = [L1, L2, COSINE, GETHIST, 
             RQueryL1, RQueryL2, RQueryCos, 
             KNNL1, KNNL2, KNNCOS]