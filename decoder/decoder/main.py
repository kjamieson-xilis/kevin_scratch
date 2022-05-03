import base64
import io
import xlrd
import pandas
import openpyxl

from mysql.connector import connect, Error

from zipfile import ZipFile, BadZipFile


def decode_mysql(number):
    try:
        with connect(
            host="labcollector-snapshot-2022-03-11.cfa8q6p9zylh.us-east-1.rds.amazonaws.com",
            user="admin",
            password="ZfhJsPbOom99SZAzu2p1",
            database="labcollector",
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"select * from modules_custom_files where file_id = '{number}'")
                result = cursor.fetchall()
                mysql_bytes = result[0][4]
                #print(type(mysql_bytes))
                with open(f'./mysql_{number}.xlsx', 'wb') as f:
                    f.write(mysql_bytes)
                #print(decoded_bytes)
                #pandas_excel = pandas.read_excel(io.BytesIO(mysql_bytes), engine="openpyxl")

    except Error as e:
        print(e)

def load_excel(filename):
    wb = openpyxl.load_workbook(filename, read_only=False, keep_vba=True)

def load_xlrd(filename):
    book = xlrd.open_workbook(filename)

def load_zipfile(filename):
    try:
        with ZipFile(filename, 'r') as f:
            print(f.infolist())

    except BadZipFile as e:
        print(e)

if __name__ == '__main__':
    #load_zipfile('/tmp/decoder/decoder/mysql_105.xlsx')
    #load_excel('/tmp/decoder/decoder/mysql_105.xlsx')
    #load_xlrd('/tmp/decoder/decoder/mysql_105.xlsx')
    load_excel('/Users/kevin/Downloads/unescaped_string.xlsx')
    #decode_mysql(104)
    #decode_mysql(105)
    #decode_mysql(106)
    #decode_mysql(107)

    #decode_mysql(73)
