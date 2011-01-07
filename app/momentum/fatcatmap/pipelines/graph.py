import sys

if 'distlib' not in sys.path:
    sys.path.insert(1, 'lib')
    sys.path.insert(2, 'distlib')

import logging

from google.appengine.ext import db

from tipfy import import_string
from momentum.fatcatmap.pipelines import FCMPipeline

from momentum.fatcatmap.models.group import Group
from momentum.fatcatmap.models.graph import NodeType
from momentum.fatcatmap.models.graph import SuperEdge
from momentum.fatcatmap.models.graph import Edge as GraphEdge
from momentum.fatcatmap.models.graph import Node as GraphNode

from momentum.fatcatmap.models.services import NodeID



class Node(FCMPipeline):

    queue_name = 'graph-worker'
    output_names = ['node','native']

    def run(self, type, label, native_kwargs={}, supernode=None, **kwargs):

        self.log.info('Creating Node')

        ## Grab NodeType record and Natural Class
        TargetNodeType = NodeType.get_by_key_name(type)
        TargetNodeNative = import_string('.'.join(TargetNodeType.native_impl_class))

        self.log.debug('Pulled NodeType "'+str(TargetNodeType)+'" with key_name "'+str(type)+'".')

        def txn():

            self.log.debug('================ TRANSACTION ================')

            ## Create Node & Extract Supernode Key
            if supernode is not None:
                node = GraphNode(supernode, label=label, type=TargetNodeType, **kwargs)
            else:
                node = GraphNode(label=label, type=TargetNodeType, **kwargs)

            ## Save Node
            db.put(node)

            ## Create Native
            native = TargetNodeNative(node, node=node)

            ## Set parameters
            if len(native_kwargs) > 0:
                for prop_name, prop_value in native_kwargs.items():
                    setattr(native, prop_name, prop_value)

            ## Save Native
            native.put()

            self.log.debug('TXN: Node Key: '+str(node.key()))
            self.log.debug('TXN: Node Inst: '+str(node))
            self.log.debug('TXN: Native Key: '+str(native.key()))
            self.log.debug('TXN: Native Inst: '+str(native))
            self.log.debug('TXN: Native Class: '+str(TargetNodeNative))

            self.log.debug('=============================================')

            ## Return values
            return (node, native)


        self.log.info('Starting transaction...')

        ## Run transaction
        node, native = db.run_in_transaction(txn)

        self.log.info('CreateNode transaction complete.')

        ## Fill named outputs
        self.fill(self.outputs.node, str(node.key()))
        self.fill(self.outputs.native, str(native.key()))

        return node.key()


class NodeGroup(FCMPipeline):

    queue_name = 'graph-worker'

    def run(self, type, name, native_args={}, plural='members', singular='member'):

        g = Group(name=name)
        if plural is not None:
            g.plural = plural
        if singular is not None:
            g.singular = singular

        group = g.put()

        yield Node(type, name, native_args, supernode=group)


class Edge(FCMPipeline):

    async = True
    queue_name = 'graph-worker'
    output_names = ['edges']

    def run(self, type, nodes, edge_kwargs={}, **kwargs):

        self.log.info('Creating Edge')

        ## Grab EdgeType record and find Implementation Class
        TargetEdgeType = EdgeType.get_by_key_name(type)
        TargetEdgeImplClass = import_string('.'.join(TargetEdgeType.edge_impl_class))

        self.log.debug('Pulled EdgeType "'+str(TargetEdgeType)+'" with key_name "'+str(type)+'".')

        if not isinstance(nodes, list) or len(nodes) != 2:
            self.log.error('Cannot connect more or less than 2 nodes. Failure.')
            raise BadValueError

        def txn():

            self.log.debug('================ TRANSACTION ================')

            ## Create Edge for each node
            edges = []
            edges.append(TargetEdgeImplClass(nodes[0], source=nodes[0], target=nodes[1], type=TargetEdgeType, **kwargs))
            edges.append(TargetEdgeImplClass(nodes[1], source=nodes[1], target=nodes[0], type=TargetEdgeType, **kwargs))

            ## Save Edges
            edge_keys = db.put(edges)

            ## Assign Partners
            edges[0].partner = edges[1]
            edges[1].partner = edges[0]

            ## Save Edges
            db.put(edges)

            self.log.debug('TXN: Edge Keys: '+str(edges))
            self.log.debug('TXN: Edge Class: '+str(TargetEdgeImplclass))
            self.log.debug('TXN: Edge Nodes: '+str(nodes))

            self.log.debug('=============================================')

            ## Get edge followup task (creates/updates an edge pair's connection record)
            task = self.get_callback_task(transactional=True)
            try:
                self.log.debug('TXN: Adding followup task "'+str(task)+'".')
                task.add(queue_name)
            except (taskqueue.TombstonedTaskError, taskqueue.TaskAlreadyExistsError):
                self.log.debug('TXN: Task followup task tombstoned or already queued:  "'+str(task)+'". Moving on.')
                pass

            ## Return values
            return edges


        self.log.info('Starting transaction...')

        ## Run transaction
        edges = db.run_in_transaction(txn)

        self.log.info('CreateEdge transaction complete.')

        ## Fill named outputs
        self.fill(self.outputs.edges, edges)

        return edges


    def callback(self):

        nodes = self.kwargs['nodes']

        self.log.info('Following up on SuperEdge health check for node pair '+str(nodes)+'...')

        node_connection = SuperEdge.all().filter('target =', nodes[0]).filter('target =', nodes[1])

        if node_connection.count() == 0:

            self.log.info('No SuperEdge exists. Creating.')

            super_edge = SuperEdge()
            super_edge.target = nodes

            key = super_edge.put()

            self.log.info('Stored SuperEdge at key "'+str(key)+'".')

        else:
            super_edge = node_connection.get()

        edges = []
        for edge in self.outputs.edges:
            super_edge.score = super_edge.score+edge.score
            edge.connection = key
            edges.append(edge)

        db.put(edges)

        self.log.info('Computed SuperEdge score: '+str(super_edge.score))
        self.log.info('SuperEdge and edges saved. Finished health check.')

        return super_edge



class NodeExtID(FCMPipeline):

    def run(self, node, service, key, value, link=None):

        service_object = db.Key.from_path('ExtService', service)
        return NodeID(node, key_name=key, name=key, value=value, link=link, service=service_object).put()