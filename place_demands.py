import csv
import sys
import py2neo

from settings import min_bps, neo4j_url


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
    routers = NodeFinder('Router')
    prefixes = NodeFinder('Prefix')
    for entry in input_data:
        bps = float(entry['bps'])
        if bps < min_bps:
            continue
        hostname = entry['hostname']
        prefix = entry['prefix']
        start_node = routers.get_node(hostname)
        prefix_node = prefixes.get_node(prefix)
        if not all((start_node, prefix_node)):
            print hostname, 'or', prefix, 'doesnt exist'
            continue
        end_node = prefixes.find_other(prefix_node, 'Router')
        print start_node.properties['name'], end_node.properties['name'], bps


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit('Specify input demands file')
    main()
