import csv
import sys

import influxdb

from settings import influxdb_host, influxdb_port, influxdb_db


def get_demands_from_influx():
    query = "select hostname, prefix, max(bps) as bps from ldp where time > now() - 30m and type = 'Ingress'  group by hostname, prefix"
    client = influxdb.InfluxDBClient(host=influxdb_host, port=influxdb_port, database=influxdb_db)
    return client.query(query)


def main():
    result = get_demands_from_influx()
    cvs_writer(result.get_points('ldp'))


def cvs_writer(results):
    fieldnames = ['hostname', 'prefix', 'bps']
    with open(sys.argv[1], 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in results:
            row = {key: entry[key] for key in fieldnames}
            writer.writerow(row)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Specify output file")
    main()
