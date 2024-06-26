import random
from collections import deque, defaultdict
import math
import numpy as np

def softmax(logits):
    x = np.array(logits)
    e_x = np.exp(x - np.max(x))  # Subtracting the maximum value for numerical stability
    return e_x / e_x.sum(axis=0)

class World:
    def __init__(self):
        self.innovations = 0
    def innovation_counter(self):
        self.innovations += 1
        return self.innovations

class Genome:
    def __init(self, world):
        self.nodes = {}
        self.connections = []

    def __init__(self, world, n_input, n_output):
        self.nodes = {}  # Dictionary where key is id and value is a dictionary with bias and type
        self.connections = []  # List of dictionaries with connection info
        self.world = world

        self.n_input = n_input 
        self.n_output = n_output

        # Create input nodes
        for i in range(n_input):
            self.nodes[i] = {'bias': 0, 'type': 0, 'activation' :0}

        # Create output nodes
        for i in range(n_output):
            self.nodes[n_input + i] = {'bias': 0, 'type': 2, 'activation': 0}

        # Create connections between input and output nodes
        for i_node in range(n_input):
            for o_node in range(n_output):
                self.connections.append({
                    'in': i_node,
                    'out': n_input + o_node,
                    'weight': random.uniform(-1, 1),
                    'enabled': True,
                    'innovation': world.innovation_counter()
                })
    def has_cycles(self, connections):
        # Build the graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for connection in connections:
            graph[connection['in']].append(connection['out'])
            in_degree[connection['out']] += 1
            if connection['in'] not in in_degree:
                in_degree[connection['in']] = 0
        
        # Queue for nodes with no incoming edges
        queue = deque([node_id for node_id in self.nodes if in_degree[node_id] == 0])
        topo_sort = []

        while queue:
            node = queue.popleft()
            topo_sort.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if there was a cycle
        if len(topo_sort) != len(self.nodes):
            return True

        return False

    def topological_order(self):
        # Build the graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        for connection in self.connections:
            graph[connection['in']].append(connection['out'])
            in_degree[connection['out']] += 1
            if connection['in'] not in in_degree:
                in_degree[connection['in']] = 0
        
        # Queue for nodes with no incoming edges
        queue = deque([node_id for node_id in self.nodes if in_degree[node_id] == 0])
        topo_sort = []

        while queue:
            node = queue.popleft()
            topo_sort.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if there was a cycle
        if len(topo_sort) != len(self.nodes):
            print(topo_sort)
            print(len(self.nodes))
            for key, value in self.nodes.items():
                print(key)
            for connection in self.connections:
                print(f"{connection['in']}, {connection['out']}")
            raise ValueError("The graph has at least one cycle")

        return topo_sort

    def apply_activation(self, node_id):
        node = self.nodes[node_id]
        activation = node['bias']
        
        for connection in self.connections:
            if connection['out'] == node_id and connection['enabled']:
                input_node = self.nodes[connection['in']]
                activation += input_node['activation'] * connection['weight']

        return activation

    def apply_network(self, inputValues):
        topo_sort = self.topological_order()
        inputs_assigned = 0
        for i in range(len(inputValues)):
            node = self.nodes[i]
            if(node['type'] == 0):
                node['activation'] = inputValues[i]
                inputs_assigned += 1
        if inputs_assigned != len(inputValues):
            raise ValueError(f"Different dimensions of first layer and input vector")
        
        for node_id in topo_sort:
            node = self.nodes[node_id] # revisar
            if(node['type'] == 1): # hidden
                activation = self.apply_activation(node_id)
                activation = math.tanh(activation)
                node['activation'] = activation

            if(node['type'] == 2): # output
                activation = self.apply_activation(node_id)
                node['activation'] = activation
        
        last_layer_activations = []

        for node_id, node in self.nodes.items():
            if(node['type'] == 2): # Esto asume que van a seguir en orden
                last_layer_activations.append(node['activation'])
        
        return last_layer_activations[0]

        """
        probabilities = softmax(last_layer_activations)
        """
        # para sensores, no aplicar no linealidad
        # aplicar softmax a outputs
        # seguir orden topológico (se puede ahorrar tiempo sacando sensores y outputs en ese orden)
        return probabilities
    

    def apply_mutation(self, p_gaussian, weight):
        if(random.random() < p_gaussian):
            new_weight = weight + random.gauss(0, 0.25)
            # print(f"changed from {weight} to {new_weight}")
            return new_weight
        else:
            new_weight = weight + random.uniform(-1, 1)
            # print(f"changed from {weight} to {new_weight}")
            return new_weight

    def alter_weights(self, p_mutation, p_gaussian):

        for node_id, node in self.nodes.items():
            if(node['type'] != 0 and random.random()<p_mutation):
                node['bias'] = self.apply_mutation(p_gaussian, node['bias'])
        for connection in self.connections:
            if(random.random()<p_mutation and connection['enabled']):
                connection['weight'] = self.apply_mutation(p_gaussian, connection['weight'])
        
        return self
    
    def add_node(self):
        connection = random.choice(self.connections)
        while(not connection['enabled']):
            connection = random.choice(self.connections)
        
        connection['enabled'] = False

        new_node_id = len(self.nodes)

        self.nodes[new_node_id] = {
            'bias' : 0,
            'type' : 1,
            'activation' : 0
        } 

        in_connection = {
            'in' : connection['in'],
            'out' : new_node_id,
            'weight' : 1,
            'innovation' : self.world.innovation_counter(),
            'enabled' : True
        }

        out_connection = {
            'in' : new_node_id,
            'out' : connection['out'],
            'weight' : connection['weight'],
            'innovation' : self.world.innovation_counter(),
            'enabled' : True
        }

        self.connections.append(in_connection)
        self.connections.append(out_connection)

        # Agarrar conexión
        # solo entre conexiones enabled
        # Del nodo de entrada, eje con peso 1 al nodo nuevo
        # Del nodo nuevo, eje con peso conexión vieja al nodo de salida
        # Deshabilitar conexión vieja
        return new_node_id

    def new_connection_valid(self, in_id, out_id):
        if in_id == out_id:
            return False
        if self.nodes[in_id] == None or self.nodes[out_id] == None:
            print(f"no {in_id} or {out_id}")
            return False

        if self.nodes[out_id]['type'] == 0:
                return False
        for connection in self.connections:
            if connection['in'] == in_id and connection['out'] == out_id:
                return False
            
        
        proxy_connection = {
            'in' : in_id,
            'out' : out_id
        }
        connections_2 = self.connections.copy()
        connections_2.append(proxy_connection)
        # print(f"checking cycles between {in_id} and {out_id}")
        return not self.has_cycles(connections_2)

    def add_connection(self):
        highest_id = len(self.nodes) - 1
        node1_id = random.randint(0,highest_id)
        node2_id = random.randint(0, highest_id)
        trials = 0
        max_trials = 100
        while not self.new_connection_valid(node1_id, node2_id):
            node1_id = random.randint(0,highest_id)
            node2_id = random.randint(0, highest_id)     
            trials += 1  
            if trials > max_trials:
                return False

        new_connection = {
            'in' : node1_id,
            'out' : node2_id,
            'weight' : random.uniform(-1,1),
            'enabled' : True,
            'innovation' : self.world.innovation_counter()
        }

        self.connections.append(new_connection)
        return new_connection['innovation']
    
    def crossing(self, other):
        my_connections = self.connections 
        others_connections = other.connections
        i = 0
        j = 0
        cross_connections = []
        new_nodes = {}
        while i < len(my_connections) and j < len(others_connections):
            my_connection = my_connections[i]
            my_innovation = my_connection['innovation']
            other_innovation = others_connections[j]['innovation']
            if my_innovation == other_innovation:
                if(random.random() > 0.5):
                    cross_connections.append(my_connection.copy())
                    my_in_node = self.nodes[my_connection['in']].copy()
                    my_out_node = self.nodes[my_connection['out']].copy()
                    new_nodes[my_connection['in']] = my_in_node
                    new_nodes[my_connection['out']] = my_out_node
                    
                else:
                    other_connection = others_connections[j].copy()
                    cross_connections.append(other_connection)
                    in_id = other_connection['in']
                    in_node = other.nodes[in_id].copy()
                    new_nodes[in_id] = in_node

                    out_id = other_connection['out']
                    out_node = other.nodes[out_id].copy() 
                    new_nodes[out_id] = out_node

                i+=1
                j+=1

            if my_innovation < other_innovation:
                cross_connections.append(my_connection.copy())
                i += 1
                my_in_node = self.nodes[my_connection['in']].copy()
                my_out_node = self.nodes[my_connection['out']].copy()
                new_nodes[my_connection['in']] = my_in_node
                
                new_nodes[my_connection['out']] = my_out_node
            if my_innovation > other_innovation:
                j += 1
        
        while i < len(my_connections):
            my_connection = my_connections[i].copy()
            cross_connections.append(my_connection)
            my_in_node = self.nodes[my_connection['in']].copy()
            my_out_node = self.nodes[my_connection['out']].copy()
            new_nodes[my_connection['in']] = my_in_node
                
            new_nodes[my_connection['out']] = my_out_node
            i += 1
        # align innovations
        # choose alleles randomly from matching genes
        # get excess and disjoint from network with higher fitness 
        new_genome = Genome(self.world, 0, 0)
        new_genome.nodes = new_nodes
        """
        for connection in cross_connections:
            new_genome.nodes[key] = {
                'bias' : value['bias'],
                'type' : value['type'],
                'activation' : value['activation']
            }
        """
        if not self.has_cycles(cross_connections):
            new_genome.connections = cross_connections
        else:
            new_genome.connections = self.connections
        
        return new_genome
    
    def genetic_distance(self, other, c1, c2, c3):
        
        excess_genes = 0
        disjoint_genes = 0
        matching_genes = 0
        weight_difference_sum = 0
        
        genome_size = max(len(self.connections), len(other.connections))

        i = 0
        j = 0
        first_matched_gene = float('inf')
        sorted_self = sorted(self.connections, key=lambda x:x['innovation'])
        sorted_other = sorted(other.connections, key=lambda x: x['innovation'])
        # print(len(sorted_self))
        # print(len(sorted_other))
        while i < len(sorted_self) or j < len(sorted_other):
            # print(i)
            # print(j)
            if(i >= len(sorted_self) or j >= len(sorted_other) and not (i >= len(sorted_self) and j >= len(sorted_other))):
                # print(i >= len(sorted_self))
                # print(j >= len(sorted_other))
                excess_genes += 1
                i +=1
                j +=1
                # print("added weird excess gene")
                continue
            
            my_innovation = sorted_self[i]['innovation']
            other_innovation = sorted_other[j]['innovation']
            if my_innovation == other_innovation:
                
                if first_matched_gene == float('inf'):
                    first_matched_gene = my_innovation
                matching_genes += 1
                weight_difference_sum += abs(sorted_self[i]['weight'] - sorted_other[j]['weight'])
                i+=1
                j+=1
                
            elif my_innovation < other_innovation:
                if my_innovation < first_matched_gene:
                    excess_genes += 1
                else:
                    disjoint_genes += 1
                i+= 1
            else:
                if other_innovation < my_innovation:
                    if other_innovation < first_matched_gene:
                        excess_genes += 1
                    else:
                        disjoint_genes += 1
                j += 1
        
        # print(excess_genes)
        # print(disjoint_genes)
        # print(weight_difference_sum)

        return c1*excess_genes/genome_size + c2*disjoint_genes/genome_size + c3*weight_difference_sum/matching_genes
    
    def copy(self):
        genoma2 = Genome(self.world, 0, 0)
        genoma2.nodes = {}
        for key, value in self.nodes.items():
            genoma2.nodes[key] = value.copy()
        for connection in self.connections:
            genoma2.connections.append(connection.copy())
        return genoma2