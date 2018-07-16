import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from utils import (get_edge_type, get_composite_owner_names,
                   get_a_composite_owner_names)


# with open('../data/PathMasterExpanded.json') as f:
#     data = json.load(f)
#
#
# df_original = pd.read_excel('../data/Composition Example.xlsx')
# df_original.dropna(how='all', inplace=True)
# # probably needs generalizing
# original_first_col_header = list(data[
#     'Columns to Navigation Map'].keys())[0]
# principal_component_set = set(df_original[original_first_col_header])
#
# for column in df_original.columns:
#     new_column_name = data['Columns to Navigation Map'][column][-1]
#     df_original.rename(columns={column: new_column_name}, inplace=True)
#
# columns_to_create = set(data['Pattern Graph Vertices']).difference(
#     set(df_original.columns))
#
# composite_thing_series = df_original['Composite Thing'].value_counts(
#     sort=False)
#
# for col in columns_to_create:
#     if col == 'composite owner':
#         df_original[col] = get_composite_owner_names(
#             prefix=col, data=composite_thing_series)
#     elif col == 'A_"composite owner"_component':
#         df_original[col] = get_a_composite_owner_names(
#             prefix=col, data=composite_thing_series)
#
# plt.figure(num=1, figsize=(30, 30))
# G = nx.DiGraph()
#
# for index, pair in enumerate(data['Pattern Graph Edges']):
#     edge_type = get_edge_type(data=data, index=index)
#     df_original[edge_type] = edge_type
#     df_temp = df_original[[pair[0], pair[1], edge_type]]
#     GraphTemp = nx.DiGraph()
#     GraphTemp = nx.from_pandas_edgelist(
#         df=df_temp, source=pair[0],
#         target=pair[1], edge_attr=edge_type,
#         create_using=GraphTemp)
#     G.add_nodes_from(GraphTemp)
#     G.add_edges_from(GraphTemp.edges, edge_attribute=edge_type)

# pos = nx.spring_layout(G)
# nx.draw_networkx(G, arrowsize=50, node_size=1000)
# edge_labels = nx.get_edge_attributes(G, 'edge type')
# nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
# plt.savefig('TestGraph.png')
# plt.show()


class Manager(object):
    """Assume the first filepath in excel_path is the "baseline" and all
    subsequent list indecies are ancestors of the baseline. The json_path
    contains the map to associate the columns of the Excel sheet to the
    dataframe columns, edge types and any missing columns."""

    def __init__(self, excel_path=[], json_path=None):
        self.excel_path = excel_path
        self.json_path = json_path
        self.json_data = None
        self.evaluators = []

    def get_json_data(self):
        with open(json_path) as f:
            self.json_data = json.load(f)

    def create_evaluators(self):
        # Evaluatior 0 is the baseline
        baseline = Evaluator(
            excel_file=excel_path[0], json_data=self.json_data)
        self.evaluators.append(baseline)

        for excel_file in range(1, len(excel_path)):
            self.evaluators.append(
                Evaluator(excel_file=excel_path[excel_file],
                          json_data=self.json_data))


class Evaluator(object):

    def __init__(self, excel_file=None, json_data=None):
        self.json_data = json_data
        self.df = pd.read_excel(excel_file)
        self.df.dropna(how='all', inplace=True)
        self.prop_di_graph = None

    def rename_excel_columns(self):
        for column in self.df.columns:
            new_column_name = self.json_data[
                'Columns to Navigation Map'][column][-1]
            self.df.rename(columns={column: new_column_name}, inplace=True)
        # TODO: make data agnostic
        for col in columns_to_create:
            if col == 'composite owner':
                self.df[col] = get_composite_owner_names(
                    prefix=col, data=composite_thing_series)
            elif col == 'A_"composite owner"_component':
                self.df[col] = get_a_composite_owner_names(
                    prefix=col, data=composite_thing_series)

    def add_missing_columns(self):
        columns_to_create = set(self.json_data[
            'Pattern Graph Vertices']).difference(
            set(df_original.columns))

        composite_thing_series = self.df['Composite Thing'].value_counts(
            sort=False)

        for col in columns_to_create:
            # TODO: find a better way
            if col == 'composite owner':
                self.df[col] = get_composite_owner_names(
                    prefix=col, data=composite_thing_series)
            elif col == 'A_"composite owner"_component':
                self.df[col] = get_a_composite_owner_names(
                    prefix=col, data=composite_thing_series)

    def to_property_di_graph(self):
        self.prop_di_graph = PropertyDiGraph()
        for index, pair in enumerate(self.json_data['Pattern Graph Edges']):
            edge_type = get_edge_type(data=self.json_data, index=index)
            self.df[edge_type] = edge_type
            df_temp = self.df[[pair[0], pair[1], edge_type]]
            GraphTemp = nx.DiGraph()
            GraphTemp = nx.from_pandas_edgelist(
                df=df_temp, source=pair[0],
                target=pair[1], edge_attr=edge_type,
                create_using=GraphTemp)
            prop_di_graph.add_nodes_from(GraphTemp)
            prop_di_graph.add_edges_from(GraphTemp.edges,
                                         edge_attribute=edge_type)

    @property
    def named_vertex_set(self):
        return self.prop_di_graph.get_vertex_set_named(df=self.df)

    @property
    def vertex_set(self):
        return self.prop_di_graph.vertex_set
