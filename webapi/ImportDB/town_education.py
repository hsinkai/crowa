# -*- coding: utf-8 -*-
import csv
import MySQLdb
from os import walk
import re
import petl
import pandas as pd
# data = pd.read_csv('okok.csv')  # 讀取csv，存入data變數
# data.drop_duplicates(keep='first', inplace=False)  # 刪除重複

# db connection
db = MySQLdb.connect(host="61.60.103.175", user="crsopr", passwd="cwb+123", db="CRSdb", charset='utf8')
cursor = db.cursor()
city_qry = """SELECT cname FROM info_city"""
cursor.execute(city_qry)
city_list = [item[0] for item in cursor.fetchall()]
town_qry = """SELECT cname FROM info_town"""
cursor.execute(town_qry)
town_list = [item[0] for item in cursor.fetchall()]
location_name_list = []

#############################
def verify_data(value_dict):
    normal_data = dict()
    # city_qry = """SELECT cname FROM info_city"""
    # cursor.execute(city_qry)
    # city_list = [item[0] for item in cursor.fetchall()]
    # town_qry = """SELECT cname FROM info_town"""
    # cursor.execute(town_qry)
    # town_list = [item[0] for item in cursor.fetchall()]

    # 1. verify special value in data
    if re.match(r'.*\?', value_dict['name']) or re.match(r'.*\?', value_dict['campus']) or \
            re.match(r'.*\?', value_dict['city']) or re.match(r'.*\?', value_dict['town']):
        with open('C:\Users\YuPing ho\PycharmProjects\crs_webapi\ImportDB\error_schooldata\error_data.csv', 'a') as csvfile:
            csvfile.write(u'\ufeff'.encode('utf8'))
            # 建立 CSV 檔寫入器
            value_dict.update({'error': 'special value'})
            writer = csv.DictWriter(csvfile, value_dict.keys())
            writer.writerow(value_dict)
            csvfile.close()

    # 2. verify city name
    elif value_dict['city'].decode('utf-8') not in city_list:
        with open('C:\Users\YuPing ho\PycharmProjects\crs_webapi\ImportDB\error_schooldata\error_data.csv', 'a') as csvfile:
            csvfile.write(u'\ufeff'.encode('utf8'))
            # 建立 CSV 檔寫入器
            value_dict.update({'error': 'wrong city name'})
            writer = csv.DictWriter(csvfile, value_dict.keys())
            writer.writerow(value_dict)
            csvfile.close()

    elif value_dict['town'].decode('utf-8') not in town_list:
        with open('C:\Users\YuPing ho\PycharmProjects\crs_webapi\ImportDB\error_schooldata\error_data.csv', 'a') as csvfile:
            csvfile.write(u'\ufeff'.encode('utf8'))
            # 建立 CSV 檔寫入器
            value_dict.update({'error': 'wrong town name'})
            writer = csv.DictWriter(csvfile, value_dict.keys())
            writer.writerow(value_dict)
            csvfile.close()
    else:
        normal_data = value_dict
    return normal_data if normal_data else None


def remove_utf8_tag(file):
    csv_file = root + '/' + file
    f = open(csv_file, "r")
    csv_data = []
    for line in f.readlines():
        data = []
        if '\xef\xbb\xbf' in line:
            str1 = line.replace('\xef\xbb\xbf', '')  # 用replace換掉'\xef\xbb\xbf'
            data.append(str1.strip())  # strip()去掉\n
            csv_data.append(data)
        else:
            data.append(line.strip())
            csv_data.append(data)
    f.close
    return csv_data


if __name__ == '__main__':

    # 指定要列出所有檔案的目錄
    mypath = "./education_data"

    # 遞迴列出所有子目錄與檔案
    for root, dirs, files in walk(mypath):
        for file in files:

            # prepare data in order to insert into db
            csv_data = remove_utf8_tag(file)
            csv_list = list(csv_data)[0:1][0]
            keys = ', '.join(csv_list)
            # keys.split(',') >>　
            # ['code', 'name', 'campus', 'location_name', 'address', 'lon', 'lat', 'city', 'town', 'education_stage']
            values = ",".join(['%s'] * len(keys.split(',')))

            value_list = []
            for x in list(csv_data)[1:]:
                normal_data = dict()
                indexpoint=0
                for index in range(len(x)):
                    value_dict = {'code': x[index].split(',')[0], 'name': x[index].split(',')[1], 'campus': x[index].split(',')[2],
                                  'location_name': x[index].split(',')[3].replace("_", "") if x[index].split(',')[3].endswith("_") else x[index].split(',')[3],
                                  'address': x[index].split(',')[4], 'lon': x[index].split(',')[5],
                                  'lat': x[index].split(',')[6], 'city': x[index].split(',')[7], 'town': x[index].split(',')[8],
                                  'education_stage': x[index].split(',')[9]}
                   #remove duplicate data
                    if value_dict['location_name'] not in location_name_list:
                        location_name_list.append(value_dict['location_name'])
                        normal_data = value_dict
                        indexpoint = 1
                    #repeat data
                    else:
                        indexpoint = 2
                        normal_data = None
                        with open(
                                'C:\Users\YuPing ho\PycharmProjects\crs_webapi\ImportDB\error_schooldata\error_data.csv',
                                'a') as csvfile:
                            csvfile.write(u'\ufeff'.encode('utf8'))
                            # 建立 CSV 檔寫入器
                            value_dict.update({'error': 'duplicate data'})
                            writer = csv.DictWriter(csvfile, value_dict.keys())
                            writer.writerow(value_dict)
                            csvfile.close()
                        # print "location_name #2"
                        # print value_dict['code']
                        break

                    # write duplicate data
                    if indexpoint == 1:
                        if verify_data(normal_data) is None:
                            # print "verify data #1"
                            # print value_dict['code']
                            break
                        elif not verify_data(normal_data):
                            # print "verify data #2"
                            # print value_dict['code']
                            value_dicts = verify_data(normal_data)
                    index_map = {v: i for i, v in enumerate(keys.split(','))}
                    datalist = []
                    for k in keys.split(','):
                        value = dict(sorted(normal_data.items(), key=lambda pair: index_map[pair[0]]))[k]
                        datalist.append(value)
                    value_list.append(datalist)
            # insert data into db
            qry = "INSERT INTO education (%s) VALUES (%s) ON DUPLICATE KEY UPDATE code=VALUES(code), " \
                  "location_name=VALUES(location_name), " \
                  "address=VALUES(address), lon=VALUES(lon), lat=VALUES(lat), " \
                  "education_stage=VALUES(education_stage) " \
                  % (keys, values)
            try:
                cursor.executemany(qry, value_list)
            except Exception as e:
                test = str(e).decode('string-escape')
            print "-------------Finished------------"
            db.commit()
db.close()
