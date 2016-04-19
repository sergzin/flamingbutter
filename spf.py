import requests
import logging
from settings import neo4j_url


def make_request(from_node, to_node):
    port_url = neo4j_url + '/' + from_node.ref + '/paths'
    request_body = {
        "to": str(to_node.resource.uri),  # destination node uri
        "cost_property": "metric",  # name of cost property
        "relationships": {
            "type": "LINK",  # relationship type
            "direction": "out"
        },
        "algorithm": "dijkstra"
    }
    result = requests.post(port_url, json=request_body)
    if result.status_code == 200:
        response = result.json()
        return response
    logging.error('SPF Error, code %s, message %s', result.status_code, result.content)
