from __future__ import print_function
import sys
import csv
import py2neo

from settings import neo4j_url


def cvs_reader(inputfile):
    fieldnames = ['hostname', 'prefix', 'bps']
    with open(inputfile, 'rb') as cvsfile:
        has_header = csv.Sniffer().has_header(cvsfile.read(1024))
        cvsfile.seek(0)
        reader = csv.DictReader(cvsfile, fieldnames=fieldnames)
        if has_header:
            next(reader)
        for row in reader:
            yield row


def cvs_writer(filename, data):
    fieldnames = ['Source', 'Destination', 'bps']
    with open(filename, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


class NodeFinder(object):
    def __init__(self, label):
        self.label = label
        self.graph = py2neo.Graph(neo4j_url)
        self.node_by_name = {}
        self.other_nodes = {}
        self._query = "match (n:{label}) where n.name =~ '{name}.*' return n"
        self._query_to_other = "match (a:{label})--(z:{other}) where id(a) = {a} return z"

    def get_node(self, name):
        if name in self.node_by_name:
            return self.node_by_name[name]
        query = self._query.format(name=name, label=self.label)
        node = self.graph.cypher.execute_one(query)
        # node = self.graph.find_one(self.label, property_key='name', property_value=name)
        self.node_by_name[name] = node
        return node

    def find_other(self, node, other_label):
        if node._id in self.other_nodes:
            return self.other_nodes[node._id]
        query = self._query_to_other.format(label=self.label, other=other_label, a=node._id)
        neighbour = self.graph.cypher.execute_one(query)
        self.other_nodes[node._id] = neighbour
        return neighbour


def main():
    input_data = cvs_reader(sys.argv[1])
    output_data = []
    routers = NodeFinder('Router')
    prefixes = NodeFinder('Prefix')
    for entry in input_data:
        bps = float(entry['bps'])
        hostname = entry['hostname']
        prefix = entry['prefix']
        start_node = routers.get_node(hostname)
        prefix_node = prefixes.get_node(prefix)
        if not start_node:
            print(hostname, 'doesnt exist')
            continue
        if not prefix_node:
            print (prefix, 'doesnt exist')
            continue
        end_node = prefixes.find_other(prefix_node, 'Router')
        output_data.append(
            {'Source': start_node.properties['name'], 'Destination': end_node.properties['name'], 'bps': bps})
    cvs_writer(sys.argv[2], output_data)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('Specify input unresolved demands file and output demands file')
    main()
