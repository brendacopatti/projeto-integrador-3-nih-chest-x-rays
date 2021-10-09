import pandas as pd
import os
import psycopg2
import constant
from skimage.exposure import histogram
from skimage.color import rgb2gray
from PIL import Image


#read and prepare data
df_x_ray = pd.read_csv(
    constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.DATA_ENTRY_CSV_FILE, 
    header=None, 
    sep=',',
    low_memory=False
)

df_x_ray[10] = ''
df_x_ray[11] = ''

df_x_ray = df_x_ray.rename({
    0: constant.IMAGE_FILE_NAME, 
    1: constant.FINDING_LABEL, 
    2: constant.FOLLOW_UP_ID, 
    3: constant.PATIENT_ID, 
    4: constant.PATIENT_AGE,
    5: constant.PATIENT_GENDER,
    6: constant.VIEW_POSITION,
    7: constant.ORIGINAL_IMAGE_WIDTH,
    8: constant.ORIGINAL_IMAGE_HEIGHT,
    9: constant.ORIGINAL_IMAGE_SPACING,
    10: constant.IMAGE_DIRECTORY_FILE_NAME,
    11: constant.PATIENT_AGE_GROUP},
    axis=1
)

for index, row in df_x_ray.iterrows():    
    images_001 = constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.IMAGES_001_DIRECTORY + '/';
    
    images_002 = constant.PROJECT_DIRECTORY + constant.DATA_DIRECTORY + constant.IMAGES_002_DIRECTORY + '/';
    
    if os.path.isfile(images_001 + row[constant.IMAGE_FILE_NAME]):
        row[constant.IMAGE_DIRECTORY_FILE_NAME] = images_001 + row[constant.IMAGE_FILE_NAME]
    elif os.path.isfile(images_002 + row[constant.IMAGE_FILE_NAME]):
        row[constant.IMAGE_DIRECTORY_FILE_NAME] = images_002 + row[constant.IMAGE_FILE_NAME]
    
df_x_ray = df_x_ray[df_x_ray[constant.IMAGE_DIRECTORY_FILE_NAME] != ""]

for index, row in df_x_ray.iterrows():    
    if (int(row[constant.PATIENT_AGE]) <= 2):
        row[constant.PATIENT_AGE_GROUP] = constant.BABIES
    elif ((int(row[constant.PATIENT_AGE]) >= 3) & (int(row[constant.PATIENT_AGE]) <= 16)):
        row[constant.PATIENT_AGE_GROUP] = constant.CHILDREN
    elif ((int(row[constant.PATIENT_AGE]) >= 17) & (int(row[constant.PATIENT_AGE]) <= 30)):
        row[constant.PATIENT_AGE_GROUP] = constant.YOUNG_ADULTS
    elif ((int(row[constant.PATIENT_AGE]) >= 31) & (int(row[constant.PATIENT_AGE]) <= 45)):
        row[constant.PATIENT_AGE_GROUP] = constant.MIDDLE_AGED_ADULTS
    else:
        row[constant.PATIENT_AGE_GROUP] = constant.OLD_ADULTS

df_patient = df_x_ray.drop_duplicates(subset=[constant.PATIENT_ID, constant.PATIENT_GENDER])

print("finalizou preparação dos dados")

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

print("finalizou create tables")

#insert data

#patient
for index, row in df_patient.iterrows():
    cur.execute(
        constant.SQL_INSERT_PATIENT, 
        (row[constant.PATIENT_ID], 
         row[constant.PATIENT_GENDER])
    )
    
con.commit()

print("finalizou inserts de pacientes")

#follow_up
for index, row in df_x_ray.iterrows():
    cur.execute(
        constant.SQL_INSERT_FOLLOW_UP, 
        (row[constant.FOLLOW_UP_ID], 
         row[constant.PATIENT_ID], 
         row[constant.PATIENT_AGE], 
         row[constant.PATIENT_AGE_GROUP], 
         row[constant.FINDING_LABEL])
    )

con.commit()

print("finalizou inserts de acompanhamentos")

#x_ray

# open as PIL image and calc histogram

def hist_calc(img_path):
    '''
    Returns histogram color 256 from a image

    Parameters
    ----------
    img_path : str
        Path for the image.

    Returns
    -------
    str
        color histogram 256 for the given image.

    '''
    im = Image.open(img_path)
    vec_str = '{'
    for item in im.histogram():
        vec_str += str(item)+', '
    vec_str = vec_str[:-2]+'}'
    
    return vec_str


print("iniciando inserts de raio-x\n\tpode demorar um pouco...")
size = df_x_ray.shape[0]
n = 0
percent = 0
for index, row in df_x_ray.iterrows():
    image = open(row[constant.IMAGE_DIRECTORY_FILE_NAME], 'rb').read()
    hist_vect = hist_calc(row[constant.IMAGE_DIRECTORY_FILE_NAME])
    cur.execute(
        constant.SQL_INSERT_X_RAY, 
        (row[constant.FOLLOW_UP_ID], 
         row[constant.PATIENT_ID],
         row[constant.VIEW_POSITION],
         psycopg2.Binary(image),
         row[constant.ORIGINAL_IMAGE_WIDTH],
         row[constant.ORIGINAL_IMAGE_HEIGHT],
         row[constant.ORIGINAL_IMAGE_SPACING],
         hist_vect)
    )
    
    if int(100*n/size) > percent:
        percent = int(100*n/size)
        print(f"{percent}%".center(10,"*"))
    n+=1
    
con.commit()

print("\tfinalizou inserts de raio-x")


#Distance, similarity, search funcs
for f in constant.FUNC_LIST:
    cur.execute(f)
print("finalizou declaração de funções no postgres")

con.close()
