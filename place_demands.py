from __future__ import print_function
import csv
import sys
import py2neo
from settings import min_bps, neo4j_url
from spf import make_request


def cvs_reader(inputfile):
    fieldnames = ['Source', 'Destination', 'bps']
    with open(inputfile, 'rb') as cvsfile:
        has_header = csv.Sniffer().has_header(cvsfile.read(1024))
        cvsfile.seek(0)
        reader = csv.DictReader(cvsfile, fieldnames=fieldnames)
        if has_header:
            next(reader)
        for row in reader:
            yield row


def main():
    graph = py2neo.Graph(neo4j_url)
    input_data = cvs_reader(sys.argv[1])
    routers = {}
    for entry in input_data:
        bps = float(entry['bps'])
        src = entry['Source']
        dst = entry['Destination']
        if min_bps and bps < min_bps:  # if min_bps defined
            continue
        start_node = routers.get(src)
        end_node = routers.get(dst)
        if not start_node:
            start_node = graph.find_one('Router', property_key='name', property_value=src)
            routers[src] = start_node
        if not end_node:
            end_node = graph.find_one('Router', property_key='name', property_value=dst)
            routers[dst] = end_node
        if not all((start_node, end_node)):
            print(src, 'or', dst, 'node missing')
            continue
        # print(start_node.properties['name'], end_node.properties['name'], bps)
        r = make_request(start_node, end_node)
        if not r:
            print("NO path between %s %s " % (start_node, end_node))
            continue
        number_of_ecmp = len(r)
        for path in r:
            print(bps / number_of_ecmp, end=' ')
            bound_nodes = [bind_node(node_url) for node_url in path['nodes']]
            graph.pull(*bound_nodes)
            map(lambda x: print(x.properties['name'], end=' '), bound_nodes)
            print(end='\n')


def bind_node(node_url):
    nd = py2neo.Node()
    nd.bind(node_url)
    return nd


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit('Specify input demands file')
    main()
