from py2neo.database import Graph
from py2neo import watch
from worker.abstract_item_processor import BaseItemProcessor

__author__ = 'pradeepv'


class SnomedConceptSynonymProcessor(BaseItemProcessor):
    statement = "MATCH (dest:Concept:FSA) WHERE dest.conceptId = {id} " \
                "CREATE (c:Concept:Synonym{conceptId: {id}, term: {term}," \
                " descType: {descType}})-[r:IS_A { relId: '116680003'," \
                " term: 'Is a (attribute)', descType: '900000000000003001'}]->(dest);"

    def __init__(self):
        #watch("neo4j.bolt")
        self.graph = Graph(bolt=True, host='localhost',
              bolt_port=11005,
              http_port=11006,
              user='neo4j',
              password='snomed')

    def process(self, record, tx):
        if record["active"] == 1: 
            activeLabel = "ACTIVE"
        else:
            activeLabel = "INACTIVE"
        tx.append(SnomedConceptSynonymProcessor.statement, {"id": record["id"],
                                                            "term": record["term"],
                                                            "descType": record["descType"]})
