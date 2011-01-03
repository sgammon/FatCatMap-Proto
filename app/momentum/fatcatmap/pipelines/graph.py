import sys
if 'distlib' not in sys.path:
    sys.path.insert(1, 'lib')
    sys.path.insert(2, 'distlib')

import logging

from google.appengine.ext import db

from tipfy import import_string
from momentum.fatcatmap.pipelines import FCMPipeline

from momentum.fatcatmap.models.graph import Node
from momentum.fatcatmap.models.graph import NodeType

from momentum.fatcatmap.models.services import NodeID

from momentum.fatcatmap.models.graph import Edge


class GraphNode(FCMPipeline):

    output_names = ['node','natural']

    def run(self, type, label, natural_kwargs={}, **kwargs):

        logging.info('GRAPHNODE: Creating GraphNode')

        ## Grab NodeType record and Natural Class
        TargetNodeType = NodeType.get_by_key_name(type)
        TargetNodeNatural = import_string('.'.join(TargetNodeType.native_impl_class))

        logging.info('GRAPHNODE: Pulled NodeType "'+str(TargetNodeType)+'" with key_name "'+str(type))

        def txn():

            logging.info('GRAPHNODE: ==== TRANSACTION ====')

            ## Create Node and Natural
            node = Node(label=label, type=TargetNodeType, **kwargs).put()
            natural = TargetNodeNatural(node, node=node)

            ## Set parameters
            if len(natural_kwargs) > 0:
                for prop_name, prop_value in natural_kwargs.items():
                    setattr(natural, prop_name, prop_value)

            natural.put()

            logging.info('GRAPHNODE: Node Key: '+str(node))
            logging.info('GRAPHNODE: Native Key: '+str(natural))
            logging.info('GRAPHNODE: Native Class: '+str(TargetNodeNatural))

            logging.info('GRAPHNODE: =====================')

            ## Return values
            return (node, natural)

        logging.info('GRAPHNODE: Starting transaction...')

        ## Run transaction
        node, natural = db.run_in_transaction(txn)

        logging.info('GRAPHNODE: Transaction complete.')

        ## Fill named outputs
        self.fill(self.outputs.node, str(node))
        self.fill(self.outputs.natural, str(natural))

        return node


class GraphEdge(FCMPipeline):

    def run(self):
        pass


class NodeExtID(FCMPipeline):

    def run(self, node, service, key, value, link=None):

        service_object = db.Key.from_path('ExtService', service)
        return str(NodeID(node, key_name=key, node=node, value=value, link=link, service=service_object).put())