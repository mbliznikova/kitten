import requests
import json

graphana_url = 'http://192.168.1.20:3000'
datasources_url = '/api/datasources/'
headers = {'content-type': 'application/json'}


def add_datasource(url, datasource_name, type, db_url, isDefault, db_name, user,
                   password):
    url += datasources_url
    datasource_data = json.dumps({"name": datasource_name, "type": type,
                                  "url": db_url, "access": "proxy",
                                  "isDefault": isDefault, "database": db_name,
                                  "user": user, "password": password})
    requests.post(url, data=datasource_data, headers=headers, auth=(user,
                                                                    password))

add_datasource(graphana_url, 'haproxy', 'influxdb', 'http://192.168.1.10:8086',
               True, 'haproxy_db', 'admin', 'admin')
