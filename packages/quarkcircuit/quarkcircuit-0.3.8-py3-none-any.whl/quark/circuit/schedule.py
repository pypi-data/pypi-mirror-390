# Copyright (c) 2024 XX Xiao

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

""" A toolkit for the dynamical decoupling."""
import copy 
import networkx as nx
from quark.circuit.basepasses import TranspilerPass
from quark.circuit.dag import qc2dag, dag2qc
from quark.circuit.quantumcircuit_helpers import (
    one_qubit_gates_available,
    two_qubit_gates_available,
    one_qubit_parameter_gates_available,
    two_qubit_parameter_gates_available,
    three_qubit_gates_available,
    functional_gates_available,
    )
from typing import Literal

class DynamicalDecoupling(TranspilerPass):
    def __init__(self,t1g,t2g):
        self.t1g = t1g
        self.t2g = t2g
        self._count = 0 # for new node 
        self._dd_start = 6

    def counter(self):

        self._count += 1
        return self._count

    def _get_max_idle_time(self,nodes):

        gates = [node.split('_')[0] for node in nodes]
        one_qubit_gates = list(one_qubit_gates_available.keys()) + list(one_qubit_parameter_gates_available.keys())
        two_qubit_gates = list(two_qubit_gates_available.keys()) + list(two_qubit_parameter_gates_available.keys())
        if bool(set(two_qubit_gates) & set(gates)):
            max_idle_time = self.t2g
        elif bool(set(one_qubit_gates) & set(gates)):
            max_idle_time = self.t1g
        else:
            max_idle_time = 0
        return max_idle_time

    def _update_idle_time(self,node,max_idle_time):

        gate = node.split('_')[0]
        if gate in one_qubit_gates_available.keys() or gate in one_qubit_parameter_gates_available.keys():
            return max_idle_time - self.t1g
        elif gate in two_qubit_gates_available.keys():
            return max_idle_time - self.t2g
        else:
            return 0

    def run(self,qc,method:Literal['XY4','XX']='XY4', align_right:bool = False, insert_before_barrier:bool = False):

        dag = qc2dag(qc,show_qubits=False)
        qubit_idle_time = {k:{'current_node':None,'idle_time':0} for k in qc.qubits}
        dag_copy = copy.deepcopy(dag)

        if align_right is True:
            topological_generations = []
            rev_dag = dag_copy.reverse()
            for nodes in nx.topological_generations(rev_dag):
                topological_generations.insert(0,nodes)
        else:
            topological_generations = nx.topological_generations(dag_copy)

        for nodes in topological_generations:
            # time
            max_idle_time = self._get_max_idle_time(nodes)
            # calcaulate
            node_qubits_dic = {node:dag_copy.nodes[node]['qubits'] for node in nodes}
            qubit_node_dic = {}
            for k,vv in node_qubits_dic.items():
                for v in vv:
                    qubit_node_dic[v] = k
            for qubit,node in qubit_node_dic.items(): # 其他qubit增加等待时间
                pre_node = qubit_idle_time[qubit]['current_node']
                idle_time = qubit_idle_time[qubit]['idle_time']
                if pre_node ==  None:
                    if idle_time > 0:
                        delay_nodes = [(f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':idle_time}),]
                        delay_edges = [(delay_nodes[0][0],node,{'qubit':[qubit]}),]
                        dag.add_nodes_from(delay_nodes)
                        dag.add_edges_from(delay_edges)
                    # update idle time
                    qubit_idle_time[qubit]['idle_time'] = self._update_idle_time(node,max_idle_time)
                    qubit_idle_time[qubit]['current_node'] = node
                else:
                    if idle_time >= self.t1g*self._dd_start:
                        if node.split('_')[0] == 'barrier' and insert_before_barrier is False:
                            # update idle time
                            qubit_idle_time[qubit]['idle_time'] = self._update_idle_time(node,max_idle_time)
                            qubit_idle_time[qubit]['current_node'] = node                        
                        else:
                            dag.remove_edge(pre_node,node)
                            if method == 'XY4':
                                tgap = (idle_time - 4*self.t1g)/5
                                dd_nodes = [(f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'y_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'y_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),]
                            elif method == 'XX':
                                tgap = (idle_time - 4*self.t1g)/5
                                dd_nodes = [(f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),(f'x_{self.counter()}_[{qubit}]',{'qubits':[qubit]}),
                                            (f'delay_{self.counter()}_[{qubit}]',{'qubits':[qubit],'duration':tgap}),]
                            dd_edges = [(dd_nodes[i][0],dd_nodes[i+1][0],{'qubit':[qubit]}) for i in range(len(dd_nodes)-1)]
                            dd_edges.append((pre_node,dd_nodes[0][0],{'qubit':[qubit]}))
                            dd_edges.append((dd_nodes[-1][0],node,{'qubit':[qubit]}))
                            dag.add_nodes_from(dd_nodes)
                            dag.add_edges_from(dd_edges)
                            # update idle time
                            qubit_idle_time[qubit]['idle_time'] = self._update_idle_time(node,max_idle_time)
                            qubit_idle_time[qubit]['current_node'] = node
                    else:
                        qubit_idle_time[qubit]['idle_time'] = self._update_idle_time(node,max_idle_time)
                        qubit_idle_time[qubit]['current_node'] = node
            for q in qubit_idle_time.keys():
                if q not in qubit_node_dic.keys():
                    qubit_idle_time[q]['idle_time'] += max_idle_time
            #print(qubit_idle_time)
            #print('=' * 35)
        qc_new = dag2qc(dag)
        return qc_new