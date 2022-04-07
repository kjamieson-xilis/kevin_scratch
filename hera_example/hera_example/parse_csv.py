import csv
import os

import boto3
from fs import filesize

s3 = boto3.resource('s3')



with open('100.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    fieldnames = csv_reader.fieldnames
    for index, row in enumerate(csv_reader):
        print(index, row.get('s3_key'))



filt_file  = open('filtered.csv', mode='w')
filtered_writer = csv.DictWriter(filt_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)

with open('100.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    buckets = {'big': 0, 'small': 0}
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            bucket, obj = os.path.split(row.get('rawImageKey'))
            bucket_name = bucket.replace('s3://','')
            s3_obj = s3.Object(bucket_name, obj)
            size = s3_obj.content_length
            if size > 50000000:
                buckets['big'] += 1
            else:
                buckets['small'] += 1
                print(row)
                filtered_writer.writerow(row)
            print(obj, filesize.binary(size))
            line_count += 1
    print(f'Processed {line_count} lines.')
    print(buckets)

filt_file.close()
