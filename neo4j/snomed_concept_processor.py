import re
from string import Template
from py2neo.database import Graph,authenticate
from py2neo import watch
from worker.abstract_item_processor import BaseItemProcessor

__author__ = 'pradeepv'


class SnomedConceptProcessor(BaseItemProcessor):
    statement = Template("CREATE (c:Concept:FSA:$label:$activeLabel {conceptId: \"$id\", term: \"$term\", descType: $descType});")
    create_index_concept_id = "CREATE INDEX ON :Concept(conceptId)"
    create_index_term = "CREATE INDEX ON :Concept(term)"

    def __init__(self):
        #watch("neo4j.bolt")
        # set up authentication parameters
        authenticate("localhost:11006", "neo4j", "snomed") # 7474, neo4j ,test
        # self.graph = Graph(super().graph_url)
        self.graph = Graph(bolt=True, host='localhost',
              bolt_port=11005,
              http_port=11006,
              user='neo4j',
              password='snomed')
        tx = self.graph.begin()
        tx.run(SnomedConceptProcessor.create_index_concept_id)
        tx.run(SnomedConceptProcessor.create_index_term)
        tx.commit()

    def process(self, record, tx):
        label = self.extract_label(record['term'])
        if label is None or label[0].isdigit():
            label = 'NO_LABEL'
        term = record["term"].replace('"','\\"')

        if record["active"] == 1 or record["active"] == "1": 
            activeLabel = "ACTIVE"
        else:
            activeLabel = "INACTIVE"

        local_statement = SnomedConceptProcessor.statement.substitute(id=record["id"], term=term,
                                                                      descType=record["descType"], label=label, activeLabel=activeLabel )
        tx.run(local_statement)

    def extract_label(self, text):
        search_match = re.search(r"\([^)]*\)$", text.rstrip())
        if search_match is not None:
            match_text = re.sub(r"[^a-zA-Z0-9_\s]", "", search_match.group(0)).upper()
            return "_".join(match_text.split())
        else:
            return None
