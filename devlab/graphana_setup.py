import requests
import json
import argparse
import os
import unittest


class Grafana(object):
    def __init__(self, grafana_url, username=None, password=None,):
        self.grafana_url = grafana_url
        self.username = username
        self.password = password
        self.content_type_headers = {'content-type': 'application/json'}

    def add_datasource(self, db_url, database, db_name, is_default=False,
                       db_access='proxy', db_type='influxdb'):
        datasource_url = self.grafana_url + '/api/datasources/'
        headers = self.content_type_headers
        datasource_data = json.dumps({"name": db_name, "type": db_type,
                                      "url": db_url, "access": db_access,
                                      "isDefault": is_default,
                                      "database": database,
                                      "user": self.username,
                                      "password": self.password})
        return requests.post(datasource_url, data=datasource_data,
                             headers=headers,
                             auth=(self.username, self.password))

    def add_panel_graph(self, *json_file):
        dashboard_url = self.grafana_url + '/api/dashboards/db'
        headers = self.content_type_headers
        vagrant_path = '/vagrant'
        if len(json_file) > 0:
            for i in range(len(json_file[0])):
                path_to_file = os.path.join(vagrant_path, json_file[0][i])
                content = open(path_to_file, 'rb').read()
                requests.post(dashboard_url, data=content,
                              headers=headers,
                              auth=(self.username, self.password))
        else:
            path_to_file = os.path.join(vagrant_path, json_file[0])
            content = open(path_to_file, 'rb').read()
            return requests.post(dashboard_url, data=content,
                                 headers=headers,
                                 auth=(self.username, self.password))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('grafana_url',  help='Address of grafana')
    parser.add_argument('datasource_url', help='Address of database')
    parser.add_argument('data_base', help='DataBase in datasource')
    parser.add_argument('db_name',
                        help='Name for database in Grafana datasource')
    parser.add_argument('--is_default_true', dest='is_default',
                        action='store_true')
    parser.add_argument('--is_default_false', dest='is_default',
                        action='store_false')
    parser.set_defaults(is_default=False)
    parser.add_argument('dashboard_json', nargs='+',
                        help='json file(s) for creating dashboard(s)')
    args = parser.parse_args()

    influx_db = Grafana(args.grafana_url, 'admin', 'admin')
    influx_db.add_datasource(args.datasource_url, args.data_base, args.db_name,
                             args.is_default)
    influx_db.add_panel_graph(args.dashboard_json)


class GrafanaTestCase(unittest.TestCase):
    def tearDown(self):
        db = requests.get('http://10.10.10.2:3000/api/dashboards/db/haproxy',
                          auth=('admin', 'admin'))
        if db.status_code == 200:
            requests.delete('http://10.10.10.2:3000/api/dashboards/db/haproxy',
                            auth=('admin', 'admin'))
        get_ds = requests.get('http://10.10.10.2:3000/api/datasources',
                              auth=('admin', 'admin'))
        datasources = json.loads(get_ds.text)
        if len(datasources) > 0:
            for i in range(len(datasources)):
                ds_id = datasources[i].get("id")
                requests.delete('http://10.10.10.2:3000/api/datasources/' +
                                str(ds_id), auth=('admin', 'admin'))

    def test_add_datasource(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        test_datasource = grafana.add_datasource('http://10.10.10.10:8086',
                                                 'haproxy_db', 'haproxy')
        self.assertEqual(test_datasource.status_code, 200)

    def test_add_dashboard(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        grafana.add_datasource('http://10.10.10.10:8086', 'haproxy_db',
                               'haproxy')
        panel_graph = grafana.add_panel_graph('graphs_dashboard.json')
        self.assertEqual(panel_graph.status_code, 200)

    def test_unauthorized(self):
        grafana = Grafana('http://10.10.10.2:3000')
        test_datasource = grafana.add_datasource('http://10.10.10.10:8086',
                                                 'haproxy_db', 'haproxy')
        self.assertEqual(test_datasource.status_code, 401)

    def test_create_datasource_without_name(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        test_datasource = grafana.add_datasource('http://10.10.10.10:8086',
                                                 'haproxy_db', '')
        self.assertEqual(test_datasource.status_code, 422)

    def test_default_dashboard(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        test_datasource = grafana.add_datasource('http://10.10.10.10:8086',
                                                 'haproxy_db', 'haproxy')
        datasource = json.loads(test_datasource.text)
        datasource_id = datasource.get("id")
        get_ds = requests.get('http://10.10.10.2:3000/api/datasources/' +
                                  str(datasource_id), auth=('admin', 'admin'))
        default_datasource = json.loads(get_ds.text)
        default_value_ds = default_datasource.get("isDefault")
        self.assertEqual(default_value_ds, False)

    def test_non_default_dashboard(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        test_datasource = grafana.add_datasource('http://10.10.10.10:8086',
                                                 'haproxy_db', 'haproxy',
                                                 is_default=True)
        datasource = json.loads(test_datasource.text)
        datasource_id = datasource.get("id")
        get_ds = requests.get('http://10.10.10.2:3000/api/datasources/' +
                              str(datasource_id), auth=('admin', 'admin'))
        non_default_datasource = json.loads(get_ds.text)
        non_default_value = non_default_datasource.get("isDefault")
        self.assertEqual(non_default_value, True)

    def test_empty_json_for_panel(self):
        grafana = Grafana('http://10.10.10.2:3000', 'admin', 'admin')
        grafana.add_datasource('http://10.10.10.10:8086', 'haproxy_db',
                               'haproxy')
        panel_graph = grafana.add_panel_graph('empty.json')
        self.assertEqual(panel_graph.status_code, 422)
