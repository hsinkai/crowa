import datetime
import time
import requests
import MySQLdb


# db connection
db = MySQLdb.connect(host="61.60.103.175",
    user="crsopr", passwd="cwb+123", db="CRSdb", charset='utf8')
cursor = db.cursor()


def http_get_url(url, pattern):
    response = requests.get(url)
    # API rate limit exceeded
    if response.status_code == 429:
        print response.status_code
        time.sleep(61)
        response = requests.get(url)
    if not response.json():
        return None
    else:
        value_list = []
        for data in response.json():
            if pattern == "AQI":
                value_dict = (dict(site_name=data['SiteName'], county=data['County'], lat=data['Latitude'],
                                      lon=data['Longitude'], aqi=data['AQI'], pollutant=data['Pollutant'],
                                      status=data['Status'], so2=data['SO2'], co=data['CO'],
                                      co_8hr=data['CO_8hr'], o3=data['O3'], o3_8hr=data['O3_8hr'], pm10=data['PM10'],
                                      pm2_5=data['PM2.5'], no2=data['NO2'], nox=data['NOx'], no=data['NO'],
                                      ws=data['WindSpeed'],wd=data['WindDirec'], publish_time=data['PublishTime'],
                                      pm2_5_avg=data['PM2.5_AVG'], pm10_avg=data['PM10_AVG']))
            elif pattern == "AQFN":
                value_dict = (dict(area=data['Area'], major_pollutant=data['MajorPollutant'], aqi=data['AQI'],
                                          forecast_date=data['ForecastDate'],
                                          minor_pollutant=data['MinorPollutant'],
                                          minor_pollutant_aqi=data['MinorPollutantAQI'],
                                          publish_time=data['PublishTime'],
                                          content=data['Content']))
            value_list.append(value_dict)
        return value_list


def insert2db(value_list, pattern):
    # insert into db
    datalist = []
    for index in range(len(value_list)):
        keys = ', '.join(value_list[index].keys())
        values = ', '.join(['%s'] * len(value_list[index].keys()))
        tup = value_list[index].values()
        datalist.append(tup)
    if pattern == "AQI":
        qry = "INSERT INTO AQI (%s) VALUES (%s) ON DUPLICATE KEY UPDATE site_name=VALUES(site_name), " \
              "county=VALUES(county), lat=VALUES(lat), lon=VALUES(lon), " \
              "aqi=VALUES (aqi), pollutant=VALUES(pollutant), status=VALUES(status), so2=VALUES(so2), " \
              "co=VALUES(co), co_8hr=VALUES(co_8hr), o3=VALUES(o3), o3_8hr=VALUES(o3_8hr), " \
              "pm10=VALUES(pm10), pm2_5=VALUES(pm2_5), no2=VALUES(no2), nox=VALUES(nox), " \
              "no=VALUES(no), ws=VALUES(ws), wd=VALUES(wd), publish_time=VALUES(publish_time), " \
              "pm2_5_avg=VALUES(pm2_5_avg), pm10_avg=VALUES(pm10_avg)" \
              % (keys, values)
    elif pattern == "AQFN":
        qry = "INSERT INTO AQFN (%s) VALUES (%s) ON DUPLICATE KEY UPDATE area=VALUES(area), " \
              "major_pollutant=VALUES(major_pollutant), aqi=VALUES(aqi), forecast_date=VALUES(forecast_date), " \
              "minor_pollutant=VALUES (minor_pollutant), minor_pollutant_aqi=VALUES(minor_pollutant_aqi)," \
              "publish_time=VALUES(publish_time), content=VALUES(content)" \
              % (keys, values)
    cursor.executemany(qry, datalist)
    print "-------------Finished------------"
    db.commit()


if __name__ == '__main__':
    
    apikey = "?apikey=dbJKVicktSCyQzg6GNUQOn9yUKV473Wv"
    AQI_url = "http://opendata.epa.gov.tw/api/v1/AQI?format=json"
    AQFN_url = "http://opendata.epa.gov.tw/api/v1/AQFN?format=json"
    AQI_list = http_get_url(AQI_url, "AQI")
    AQFN_list = http_get_url(AQFN_url, "AQFN")
    # insert into db
    insert2db(AQI_list, "AQI")
    insert2db(AQFN_list, "AQFN")
db.close()
