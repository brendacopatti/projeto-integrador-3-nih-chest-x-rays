import pandas as pd
import os
import psycopg2
import constant

#read and prepare data
df_x_ray = pd.read_csv(
    constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.DATA_ENTRY_CSV_FILE, 
    header=None, 
    sep=','
)

df_x_ray[10] = ''

df_x_ray = df_x_ray.rename({
    0: 'image_file_name', 
    1: 'finding_label', 
    2: 'follow_up_id', 
    3: 'patient_id', 
    4: 'patient_age',
    5: 'patient_gender',
    6: 'view_position',
    7: 'original_image_width',
    8: 'original_image_height',
    9: 'original_image_pixel_spacing',
    10: 'image_directory_file_name'},
    axis=1
)

for index, row in df_x_ray.iterrows():
    images_001 = constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.IMAGES_001_DIRECTORY + '/';
    
    images_002 = constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.IMAGES_002_DIRECTORY + '/';
    
    if os.path.isfile(images_001 + row['image_file_name']):
        print("aq 1")
        row['image_directory_file_name'] = images_001 + row['image_file_name']
    elif os.path.isfile(images_002 + row['image_file_name']):
        print("aq 2")
        row['image_directory_file_name'] = images_002 + row['image_file_name']
    
df_x_ray = df_x_ray[df_x_ray['image_directory_file_name'] != ""]

df_patient = df_x_ray.drop_duplicates(subset=['patient_id', 'patient_gender'])

#connect database
con = psycopg2.connect(
    host=constant.POSTGRESQL_HOST, 
    database=constant.POSTGRESQL_DATABASE,
    user=constant.POSTGRESQL_USER, 
    password=constant.POSTGRESQL_PASSWORD
)

cur = con.cursor()

#create tables

cur.execute(constant.SQL_DROP_X_RAY)

cur.execute(constant.SQL_DROP_FOLLOW_UP)

cur.execute(constant.SQL_DROP_PATIENT)

cur.execute(constant.SQL_CREATE_PATIENT)

cur.execute(constant.SQL_CREATE_FOLLOW_UP)

cur.execute(constant.SQL_CREATE_X_RAY)

con.commit()

#insert data

#patient
for index, row in df_patient.iterrows():
    cur.execute(
        constant.SQL_INSERT_PATIENT, 
        (row['patient_id'], 
         row['patient_gender'])
    )
    
con.commit()

#follow_up
for index, row in df_x_ray.iterrows():
    cur.execute(
        constant.SQL_INSERT_FOLLOW_UP, 
        (row['follow_up_id'], 
         row['patient_id'], 
         row['patient_age'], 
         row['finding_label'])
    )

con.commit()

#x_ray
for index, row in df_x_ray.iterrows():
    image = open(row['image_directory_file_name'], 'rb').read()
    cur.execute(
        constant.SQL_INSERT_X_RAY, 
        (row['follow_up_id'], 
         row['patient_id'],
         row['view_position'],
         psycopg2.Binary(image),
         row['original_image_width'],
         row['original_image_height'],
         row['original_image_pixel_spacing'])
    )

con.commit()



