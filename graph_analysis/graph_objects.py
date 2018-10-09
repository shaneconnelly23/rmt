import networkx as nx

from .utils import get_node_types_attrs


UML_ID = {
    'count': 0
}


def get_uml_id(name=None):
    """Returns the UML_ID for the corresponding vertex name provided. If the
    name provided does not exist as a key in the UML_ID dictionary than a
    new key is created using that name and the value increments with
    new_<ith new number>.

    Parameters
    ----------
    name : string
        The Vertex.name attribute

    Notes
    -----
    This will be updated to become a nested dictionary
    with the first key being the name and the inner key will be the
    new_<ith new number> key and the value behind that will be the UUID created
    by MagicDraw.
    """
    # TODO: make this a generator function
    if name in UML_ID.keys():
        return UML_ID[name]
    else:
        UML_ID.update({name: 'new_{0}'.format(UML_ID['count'])})
        UML_ID['count'] += 1
        return UML_ID[name]


def create_vertex_objects(df=None, graph=None):
    """Returns a list of Vertex objects. Seems to be depricated in favor of
    get_node_types_attrs(), however this function is still used in testing.

    Parameters
    ----------
    df : Pandas DataFrame
        The DataFrame from the Evaluator after the implied nodes have been
        created.

    graph : PropertyDiGraph
        The Property Directed Graph that the Vertices should be created from.

    Notes
    -----
    Once this has definitively been identified as a depricated function it will
    be removed.
    """
    vertex_list = []
    for node in graph.nodes:
        mask = df == node
        node_type_columns = df[mask].dropna(
            axis=1, how='all').columns
        node_types = {col for col in node_type_columns}
        vertex = Vertex(name=node, node_types=node_types,
                        successors=graph.succ[node].copy(),
                        predecessors=graph.pred[node].copy())
        vertex_list.append(vertex)

    return vertex_list


class PropertyDiGraph(nx.DiGraph):
    """
    Class for aggregating the Excel data from the Evaluator into a Directed
    Graph with node and edge properties.

    PropertyDiGraph inherits from networkx.DiGraph to utilize the NetworkX
    framework for building a graph with from_pandas_edgelist() and for the
    data aggregation advantages of the NetworkX framework.

    Since this inherits directly from nx.DiGraph, the functions and attributes
    documented in the NetworkX documenation applies to any PropertyDiGraph
    object.

    Parameters
    ----------
    incoming_graph_data : input graph
        Data to initialize the graph. If None is supplied than an empty graph
        is created. The data can be any format supported by to_networkx_graph()

    root_attr_columns : set
        Set of columns from the Excel file that do not appear under the
        'Columns to Navigation Map' and should be applied to the root node
        as additional attributes.

    Properties
    ----------
    named_vertex_set : set
        Returns a set of elements Vertex.name from the vertex_set attribute.

    named_edge_set : set
        Returns a set of elements that are named edge 3-tuples with
        (<source name>, <target name>, edge attribute), built from the DiEdge
        property that returns the in this form.

    Attributes
    ----------
    vertex_dict : dictionary
        dictionary with the keys as the Vertex name and the value as the
        vertex object.

    vertex_set : set
        set comprised of instances of the Vertex class.

    edge_set : set
        set comprised of instances of the DiEdge class.

    root_attr_columns : set
        set comprised of column names from the Excel file that are not found in
        the JSON file, could be empty.

    See Also
    --------
    networkx.Graph
    networkx.DiGraph

    Notes
    -----
    This class serves as a data aggregation class for the Vertex and DiEdge
    classes by making sense of the DataFrame data and providing a convenient
    structure to feed the two aforementioned classes.
    Furthermore, instances of subgraphs of this class will be leveraged with
    the is_isomorphic() method to define changes between a baseline and
    ancestor.
    """

    def __init__(self, incoming_graph_data=None,
                 root_attr_columns=None, ** attr):
        self.vertex_dict = {}
        self.edge_dict = {}
        self.vertex_set = set()
        self.edge_set = set()
        self.root_attr_columns = root_attr_columns
        super().__init__(incoming_graph_data=None)
        # TODO: these two attribtues caused my Evaluator tests to fail
        # TODO: figure out a way to set these attrs without creating in init
        # self.create_vertex_set()
        # self.create_edge_set()

    @property
    def named_vertex_set(self):
        """Returns a set of vertex name attributes from the set of vertex
        objects created during the create_vertex_set method.
        """
        vert_set_named = set()
        for vert in self.vertex_set:
            vert_set_named.add(vert.name)
        return vert_set_named

    @property
    def named_edge_set(self):
        """Returns a set of named edge triples of the form (source name,
        target name, edge attribute) from the edge objects in the edge_set.
        """
        return {edge.named_edge_triple for edge in self.edge_set}

    def create_vertex_set(self, df=None, root_node_type=None):
        """Returns a vertex_set containing all of the vertex objects created
        from the Graph.nodes attribute.

        Parameters
        ----------
        df : Pandas DataFrame
            The Evaluator.df to type the nodes based on all of the columns a
            particular node is found under.

        root_node_type : set
            The Evaluator.root_node_attr_columns attribute that lists all of
            the columns present in the DataFrame that do not show up in the
            JSON as part of the pattern graph. These columns are assumed to be
            additional attributes attached to the root node.

        Notes
        -----
        This function iterates through all of the nodes in the Graph, gets
        their node type from the DataFrame column they can be found in and
        creates a Vertex object using the information from that node.
        Finally, this function creates a vertex dictionary with the Vertex.name
        as the key and the vertex object as the value.
        """
        for node in self.nodes:
            node_type_columns, node_attr_dict = get_node_types_attrs(
                df=df,
                node=node,
                root_node_type=root_node_type,
                root_attr_columns=self.root_attr_columns)

            node_types = {col for col in node_type_columns}
            vertex = Vertex(name=node, node_types=node_types,
                            successors=self.succ[node],
                            predecessors=self.pred[node],
                            attributes=node_attr_dict)
            self.vertex_dict.update({node: vertex})
            self.vertex_set.add(vertex)

        return self.vertex_set

    def create_edge_set(self):
        """Creates an edge set comprised of edge objects.
        """
        edge_pair_attr_dict = nx.get_edge_attributes(self, 'edge_attribute')
        for edge_pair in edge_pair_attr_dict:
            source_vert = self.vertex_dict[edge_pair[0]]  # the object
            target_vert = self.vertex_dict[edge_pair[1]]  # the object
            edge = DiEdge(source=source_vert,
                          target=target_vert,
                          edge_attribute=edge_pair_attr_dict[edge_pair])
            self.edge_dict.update(
                {(source_vert.name, target_vert.name,
                    edge_pair_attr_dict[edge_pair]): edge})
            self.edge_set.add(edge)


class Vertex(object):
    """
    Class for representing the node data from the PropertyDiGraph as an object.

    Vertex provides convenient access to the properties of the nodes in the
    PropertyDiGraph and critically provides the method for packaging itself
    for the MagicDraw interface layer.

    Properties
    ----------
    connections : list
        List of dictionaries with successors first and predecessors after. The
        dictionaries contain source, target key value pairs.

    Parameters
    ----------
    name : string
        Name attribute of the vertex object that is the same as the name in the
        Evaluator.df entires.

    node_types : set
        Set of strings that reflects the names of the columns under which
        the name of this vertex can be found in the Evaluator.df

    successors : set
        Set of successors saved off from the PropertyDiGraph

    predecessors : set
        Set of predecessors saved off from the PropertyDiGraph

    attribtues : dictionary
        Dictionary holding the data encapsulated in the root_node_attr_columns

    Notes
    -----
    This class encapsulates the node data from the PropertyDiGraph, providing
    user defined functions for accessing the information of a particular
    Vertex. Additionally, this class contains the to_uml_json() method which,
    packages the Vertex for the MagicDraw interface layer.
    """

    def __init__(self, name=None, node_types=set(),
                 successors=None, predecessors=None,
                 attributes=None):
        self.name = name
        self.node_types = node_types
        self.successors = successors
        self.predecessors = predecessors
        self.attributes = attributes

    @property
    def connections(self):
        """Returns a list of dictionaries with key value pairs for source and
        target node names.
        """
        connections = []
        # {'<node name>' : {'edge_attribute': 'edge type'}}
        for node_name in self.successors:
            temp_dict = {'source': self.name,
                         'target': node_name}
            temp_dict.update(self.successors[node_name])
            connections.append(temp_dict)
        for node_name in self.predecessors:
            temp_dict = {'source': node_name,
                         'target': self.name}
            temp_dict.update(self.predecessors[node_name])
            connections.append(temp_dict)
        return connections

    def to_dict(self):
        """Produces a dictionary for the attributes. Primarily used to test that
        the object was created properly.
        """
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors,
                'attributes': self.attributes}

    def to_uml_json(self, translator=None):
        """Returns two lists of dictionaries formatted for JSON output to the
        MagicDraw interface layer. The first list returned contains the vertex
        and its values with additional subdictionaries if that particular
        Vertex had more than one node_type. The second list returned contains
        all of the connections of the Vertex.

        Parameters
        ----------
        translator : MDTranslator Object
            A MDTranslator object that prvoides access to the
            JSON data file that translates the information from the Python
            meanigns here to MagicDraw terminology.

        Notes
        -----
        First, the function loops over the node_types attribute. For the first
        node_type attribute encountered (regardless of its value), the metadata
        associated with that node_type is recorded. Subsequent loop iterations
        provide additional node_type information.
        Next, the edge_uml_list is built using the connections property. From
        there, a source and target id are identified from the connections
        information and the get_uml_id function.
        With both of these lists populated, the function returns the
        node_uml_list and the edge_uml_list to be packaged for the final JSON
        output. The JSON file contains all of the vertex data first followed by
        the edge data.
        """
        # TODO: if op == create then metatype should be a key value should not
        # TODO: if op == replace then value should be a key metatype should not
        node_uml_list = []

        for count, node_type in enumerate(self.node_types):
            if count == 0:
                node_uml_dict = {
                    'id': translator.get_uml_id(name=self.name),
                    'ops': [
                        {
                            'op': 'create',  # evaluator replace with fn input.
                            'name': self.name,
                            'path': None,
                            'metatype': translator.get_uml_metatype(
                                node_key=node_type),
                            'stereotype': translator.get_uml_stereotype(
                                node_key=node_type),
                            'attributes': self.attributes
                        }
                    ]
                }
            path_val, settings_val = translator.get_uml_settings(
                node_key=node_type)
            if settings_val and count != 0:
                decorations_dict = {
                    'op': 'replace',
                    'path': path_val,
                    'value': settings_val,
                }
                node_uml_dict['ops'].append(decorations_dict)
            elif settings_val and count == 0:
                node_uml_dict['ops'][0].update({'path': path_val,
                                                'value': settings_val})
            else:
                continue

        node_uml_list.append(node_uml_dict)

        # check the connections.
        edge_uml_list = []
        for connection in self.connections:
            edge_uml_dict = {
                'id': translator.get_uml_id(name=connection['source']),
                'ops': [
                    {
                        'op': 'replace',
                        'path': '/' + connection['edge_attribute'],
                        'value': translator.get_uml_id(name=connection['target']),
                    }
                ]
            }
            edge_uml_list.append(edge_uml_dict)

        return node_uml_list, edge_uml_list


class DiEdge(object):
    """A Directed Edge object stores the source and target vertex objects
    along with the edge attribute connecting the two.
    This Class was created to facilitate the graph difference exploration
    The Directed Edges are returned as triples (source, target, edge_attribtue)

    Properties
    ----------
    named_edge_triple : tuple
        Triple with the source.name and target.name attributes and the
        edge_attribute string.

    edge_vert_type_triple : tuple
        The triple with the source.node_types and target.node_types attributes
        and the edge_attribute string. Should this property be updated to
        return multiple triples if there are multiple node_types?

    edge_triple : tuple
        The triple with the source and target Vertex objects and the
        edge_attribute string.

    Attributes
    ----------
    source : Vertex
        The Vertex at the tail of the directed edge
    target : Vertex
        The Vertex at the tip fo the directed edge
    edge_attribute : string
        The string that describes the edge type
    """

    def __init__(self, source=None, target=None, edge_attribute=None):
        # Source, Target and attr are actually strings not objects.
        self.source = source
        self.target = target
        self.edge_attribute = edge_attribute

    @property
    def named_edge_triple(self):
        return (self.source.name, self.target.name, self.edge_attribute)

    @property
    def edge_vert_type_triple(self):
        return (self.source.node_types,
                self.target.node_types,
                self.edge_attribute)

    @property
    def edge_triple(self):
        return (self.source, self.target, self.edge_attribute)
