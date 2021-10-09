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
SQL_CREATE_X_RAY='create table if not exists x_ray(follow_up_id integer not null, patient_id integer not null, view_position char(2), image bytea, original_image_width decimal(7,2),	original_image_height decimal(7,2),	original_image_pixels decimal(10,8), constraint pk_x_ray primary key (follow_up_id, patient_id), constraint fk_follow_up foreign key (follow_up_id, patient_id) references follow_up(id, patient_id));'

#INSERT DATA
SQL_INSERT_PATIENT='insert into patient(id, gender) values (%s, %s);'
SQL_INSERT_FOLLOW_UP='insert into follow_up(id, patient_id, patient_age, patient_age_group, finding_label) values (%s, %s, %s, %s, %s);'
SQL_INSERT_X_RAY='insert into x_ray(follow_up_id, patient_id, view_position, image, original_image_width, original_image_height, original_image_pixels) values (%s, %s, %s, bytea(%s), %s, %s, %s)'

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

