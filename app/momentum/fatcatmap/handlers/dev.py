import os
import simplejson as json

from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.api import taskqueue

from momentum.fatcatmap.handlers import FCMRequestHandler
from momentum.fatcatmap.models.graph import Node
from momentum.fatcatmap.models.graph import Edge
from momentum.fatcatmap.models.graph import Graph


class SandboxIndex(FCMRequestHandler):
    def get(self):
        return self.render('sandbox/main.html', dependencies=['Protovis'])


class SandboxManageData(FCMRequestHandler):
    def get(self):
        return self.render('sandbox/addData.html')


class SandboxProcedure(FCMRequestHandler):
    def get(self, procedure=None):

        if procedure == None:
            return self.response('<b>Procedure empty. Fail.</b>')
        else:
            if procedure == 'simple':
                g = Graph(key_name='simple', name='Simple').put()

                one = Node(g, key_name='one', label='One').put()
                two = Node(g, key_name='two', label='Two').put()
                three = Node(g, key_name='three', label='Three').put()
                four = Node(g, key_name='four', label='Four').put()
                five = Node(g, key_name='five', label='Five').put()
                six = Node(g, key_name='six', label='Six').put()
                seven = Node(g, key_name='seven', label='Seven').put()
                eight = Node(g, key_name='eight', label='Eight').put()
                nine = Node(g, key_name='nine', label='Nine').put()
                ten = Node(g, key_name='ten', label='Ten').put()
                node_keys = [one, two, three, four, five, six, seven, eight, nine, ten]

                edges = []
                edges.append(Edge(g, key_name='one', nodes=[one, two]))
                edges.append(Edge(g, key_name='two', nodes=[one, three]))
                edges.append(Edge(g, key_name='three', nodes=[one, six]))
                edges.append(Edge(g, key_name='four', nodes=[six, seven]))
                edges.append(Edge(g, key_name='five', nodes=[six, eight]))
                edges.append(Edge(g, key_name='six', nodes=[six, nine]))
                edges.append(Edge(g, key_name='seven', nodes=[six, ten]))
                edges.append(Edge(g, key_name='eight', nodes=[ten, four]))
                edges.append(Edge(g, key_name='nine', nodes=[four, five]))
                edge_keys = db.put(edges)

                return self.render('sandbox/addData.html', injected_data=True, nodes=node_keys, edges=edge_keys, graphs=[g])

            elif procedure == 'sunlight':
                token = channel.create_channel('admin-sandbox-'+os.environ['REMOTE_ADDR'])

                t = taskqueue.Task(url=self.url_for('workers-sunlight', procedure='getLegislators'), params={'channel':'admin-sandbox-'+os.environ['REMOTE_ADDR']})
                t.add('sunlightlabs-worker')

                return self.render('sandbox/sunlightConsole.html', channel_token=token)

            elif procedure == 'basedata':

                from momentum.fatcatmap.dev.default_data import all_functions

                proc_result = []
                for fxn in all_functions:

                   resulting_keys = fxn()
                   proc_result.append('Successfully ran function '+str(fxn)+' and stored resulting '+str(len(resulting_keys))+' keys.')


                return self.render('sandbox/basedata.html', result='<li>'+'</li><li>'.join(proc_result)+'</li>')

        return self.response('<b>Procedure: '+str(procedure)+'</b>')


class SandboxGraphQuery(FCMRequestHandler):

    def get(self):
        
        nodes = Node.all().fetch(50)
        edges = Edge.all().fetch(50)

        nodes_index = []
        nodes_list = []
        for node in nodes:
            nodes_index.append(node.key())
            if node.parent() is not None:
                parent = node.parent().kind() + ' // ' + node.parent().key().id_or_name()
            else:
                parent = str(None)
            nodes_list.append({'nodeName': node.label, 'group': 1,
                               'nodeKey': {'kind': node.kind(), 'value': str(node.key()),
                                           'id_or_name': node.key().id_or_name(), 'parent': parent}})

        edges_list = []
        for edge in edges:
            node_alpha = edge.nodes[0]
            node_beta = edge.nodes[1]

            edges_list.append(
                        {'source': nodes_index.index(node_alpha), 'target': nodes_index.index(node_beta), 'value': 1})

        data = {'nodes': nodes_list, 'links': edges_list}

        json_obj = json.dumps(data)

        r = self.response(self.render_template('sandbox/js/simpleGraph.js', data=json_obj))
        r.headers['Content-Type'] = 'application/javascript'

        return r