from lxml import objectify
from py2neo import Graph, Relationship
import sys
from settings import neo4j_url
# import logging

# logging.basicConfig(format='%(asctime)s %(name)s %(message)s', level=logging.INFO)

max_isis_metric = 16777215  # (2**24)-1


def main(graph):
    # logging.info("starting")
    # logging.info("Neo4j db size: %s", graph.size)
    input_file = sys.argv[1]
    root = objectify.parse(input_file).getroot()
    for isis_entry in root.findall('.//{*}isis-database-entry'):
        current_node = isis_entry['lsp-id'].pyval[:-3]
        router_node = graph.merge_one('Router', property_key='name', property_value=current_node)
        lsp_attrib = isis_entry.find('.//{*}isis-packet/{*}lsp-attributes')
        overload_bit = True if lsp_attrib and 'Overload' in lsp_attrib.pyval else False
        for prefix in isis_entry.findall('.//{*}isis-prefix'):
            ip_prefix = prefix['address-prefix'].pyval
            metric = max_isis_metric if overload_bit else prefix['metric'].pyval
            # logging.debug("Got ISIS IP Prefix: %s %s %s", current_node, ip_prefix, metric)
            ip_node = graph.merge_one('Prefix', property_key='name', property_value=ip_prefix)
            path = Relationship(ip_node, 'ISIS', router_node, metric=metric)
            graph.create_unique(path)
        for isis_neighbour in isis_entry.findall('.//{*}isis-neighbor'):
            neighbour = isis_neighbour['is-neighbor-id'].pyval
            metric = max_isis_metric if overload_bit else isis_neighbour['metric'].pyval
            # logging.debug("Got ISIS Neighbour: %s %s %s", current_node, neighbour, metric)
            neighbour_node = graph.merge_one('Router', property_key='name', property_value=neighbour)
            neighbourship = Relationship(router_node, 'LINK', neighbour_node, metric=metric)
            graph.create_unique(neighbourship)


def create_schema(graph):
    if 'name' not in graph.schema.get_uniqueness_constraints('Router'):
        graph.schema.create_uniqueness_constraint("Router", "name")
    if 'name' not in graph.schema.get_uniqueness_constraints('Prefix'):
        graph.schema.create_uniqueness_constraint("Prefix", "name")


if __name__ == '__main__':
    g = Graph(neo4j_url)
    create_schema(g)
    main(g)
