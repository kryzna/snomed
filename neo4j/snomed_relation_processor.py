from py2neo.database import Graph
from py2neo import watch
from worker.abstract_item_processor import BaseItemProcessor
from string import Template

__author__ = 'pradeepv'


class SnomedRelationProcessor(BaseItemProcessor):
    statement = Template("MATCH (source:Concept:FSA) WHERE source.conceptId = '$sourceId' " \
                         "MATCH (dest:Concept:FSA) WHERE dest.conceptId = '$destinationId' " \
                         "CREATE (source)-[r:$label{relId:'$typeId', term: '$term', descType: '$descType', active: '$activeLabel'}]->(dest)")


    def __init__(self):
        #watch("neo4j.bolt")
        self.graph = Graph(bolt=True, host='localhost',
              bolt_port=11005,
              http_port=11006,
              user='neo4j',
              password='snomed')


    def process(self, record, tx):
        if record["active"] == 1 or record["active"] == "1": 
            activeLabel = "ACTIVE"
        else:
            activeLabel = "INACTIVE"        
        local_statement = SnomedRelationProcessor.statement.substitute(sourceId=record['sourceId'],
                                                                   destinationId=record['destinationId'],
                                                                   label=record['relLabel'],
                                                                   typeId=record['typeId'],
                                                                   term=record['term'],
                                                                   descType=record['descType'],
                                                                   activeLabel=activeLabel)
        tx.run(local_statement)
