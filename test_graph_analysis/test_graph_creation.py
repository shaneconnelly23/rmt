import unittest
import os
import json
import pandas as pd

from graph_analysis.graph_creation import (Manager, Evaluator, MDTranslator)
from graph_analysis.graph_objects import DiEdge, PropertyDiGraph, Vertex


DATA_DIRECTORY = '../data/'


# class TestProduceJson(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_json_creation(self):
#         manager = Manager(excel_path=[os.path.join(
#             DATA_DIRECTORY, 'Sample Equations.xlsx')],
#             json_path=os.path.join(DATA_DIRECTORY,
#                                    'ParametricGraphMaster.json'))
#         translator = manager.translator
#         evaluator = manager.evaluators[0]
#         evaluator.rename_df_columns()
#         evaluator.add_missing_columns()
#         evaluator.to_property_di_graph()
#         property_di_graph = evaluator.prop_di_graph
#         property_di_graph.create_vertex_set(
#             df=evaluator.df, root_node_type=translator.get_root_node())
#         vert_set = property_di_graph.vertex_set
#         json_out = {'modification targets': []}
#         edge_json = []
#         for vertex in vert_set:
#             vert_uml, edge_uml = vertex.to_uml_json(translator=translator)
#             json_out['modification targets'].extend(vert_uml)
#             edge_json.extend(edge_uml)
#
#         json_out['modification targets'].extend(edge_json)
#         with open(os.path.join(DATA_DIRECTORY,
#                                'changes_uml.json'), 'w') as outfile:
#             json.dump(json_out, outfile, indent=4)
#
#     def tearDown(self):
#         pass


class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(
            excel_path=[os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx')
                for i in range(2)],
            json_path=os.path.join(DATA_DIRECTORY,
                                   'CompositionGraphMaster.json'))

    def test_get_json_data(self):
        expected_keys = ['Columns to Navigation Map',
                         'Pattern Graph Vertices',
                         'Pattern Graph Edge Labels',
                         'Pattern Graph Edges',
                         'Pattern Spanning Tree Edges',
                         'Pattern Spanning Tree Edge Labels',
                         'Root Node',
                         'Vertex MetaTypes',
                         'Vertex Stereotypes',
                         'Vertex Settings']

        self.assertListEqual(expected_keys, list(
            self.manager.json_data.keys()))

    def test_create_evaluators(self):
        # weak test: create_evaluators() run during init
        self.assertEqual(2, len(self.manager.evaluators))
        for eval in self.manager.evaluators:
            self.assertIsInstance(eval, Evaluator)

    def test_get_pattern_graph_diff(self):
        # this is a bad function and an improper test.
        # The test ignores the obvious problem of non-unique matchings
        # TODO: develop a stronger algorithm that ensures unique pairings
        # and lists nonunique pairings.
        base_inputs = [('s1', 't1', 'type'),
                       ('s12', 't12', 'memberEnd'),
                       ('song', 'tiger', 'blue'), ]

        ancestor = [('as1', 't1', 'type'),
                    ('s12', 'at12', 'memberEnd'), ('b', 'c', 'orange')]

        # this will cause to fail because matching is not unique.
        # ancestor = [('as1', 't1', 'type'), ('s1', 'at2', 'type'),
        #             ('as3', 't3', 'owner'), ('s4', 'at4', 'owner'),
        #             ('as5', 't5', 'memberEnd'),
        #             ('s6', 'at6', 'memberEnd'),
        #             ('as7', 't7', 'type'), ('s8', 'at8', 'type'),
        #             ('as9', 't9', 'owner'), ('s10', 'at10', 'owner'),
        #             ('as11', 't11', 'memberEnd'),
        #             ('s12', 'at12', 'memberEnd'), ('b', 'c', 'orange')]

        base_edges = []
        ancestor_edges = []

        for edge_tuple in base_inputs:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            base_edges.append(edge)

        for edge_tuple in ancestor:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            ancestor_edges.append(edge)

        self.manager.evaluators[0].prop_di_graph = PropertyDiGraph()
        self.manager.evaluators[1].prop_di_graph = PropertyDiGraph()
        self.manager.evaluators[0].prop_di_graph.edge_set = set(base_edges)
        self.manager.evaluators[1].prop_di_graph.edge_set = set(ancestor_edges)

        # base_map = dict((ea.edge_attribute, list()) for ea in base_edges)
        #
        # ance_map = dict((ea.edge_attribute, list()) for ea in ancestor_edges)
        #
        # for edge in base_edges:
        #     base_map[edge.edge_attribute].append(edge)
        # for edge in ancestor_edges:
        #     ance_map[edge.edge_attribute].append(edge)
        #
        # base_preference = {}
        # ancestor_preference = {}
        #
        # for edge in base_edges:
        #     if edge.edge_attribute not in ance_map.keys():
        #         base_preference[edge] = []
        #     else:
        #         base_preference[edge] = base_map[edge.edge_attribute]
        # for edge in ancestor_edges:
        #     if edge.edge_attribute not in base_map.keys():
        #         ancestor_preference[edge] = []
        #     else:
        #         ancestor_preference[edge] = base_map[edge.edge_attribute]
        #
        # base_matches = match_changes(change_dict=base_preference)
        # ance_matches = match_changes(change_dict=ancestor_preference)
        #
        # for no_match in base_matches['no matches']:
        #     ance_matches['no matches'].append(no_match)
        #
        match_dict = self.manager.get_pattern_graph_diff()
        match_dict_str = {}
        for key in match_dict['0 and 1'].keys():
            if key != 'no matches':
                match_dict_str.update(
                    {key.named_edge_triple: match_dict[
                        '0 and 1'][key].named_edge_triple})
        # match_dict_str.update({'no matches': match_dict['no matches']})
        no_match_to_str = []
        for value in match_dict['0 and 1']['no matches']:
            no_match_to_str.append(value.named_edge_triple)

        match_dict_str.update({'no matches': no_match_to_str})

        expected_matches = {('s1', 't1', 'type'): ('as1', 't1', 'type'),
                            ('s12', 't12', 'memberEnd'): ('s12',
                                                          'at12', 'memberEnd'),
                            'no matches': [('b', 'c', 'orange'),
                                           ('song', 'tiger', 'blue')]}
        self.assertDictEqual(expected_matches, match_dict_str)

    def tearDown(self):
        pass


class TestEvaluator(unittest.TestCase):
    # TODO: Make sure all additional graph objects that are desired are
    # created by the graph creation logic.
    # TODO: Test the PROCESS of some of these functions.

    def setUp(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        self.translator = MDTranslator(json_data=data)
        self.evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            translator=self.translator)

        data_dict = {
            'Component': ['Car', 'Car', 'Car', 'Car', 'Car', 'Car',
                          'Car', 'Wheel', 'Wheel', 'Wheel', 'Engine',
                          'Engine', 'Engine', 'Engine', 'Engine', 'Engine', ],
            'Position': ['engine', 'chassis', 'driveshaft', 'front passenger',
                         'front driver', 'rear passenger', 'rear driver',
                         'hub', 'tire', 'lug nut', 'one', 'two', 'three',
                         'four', 'drive output', 'mount'],
            'Part': ['Engine', 'Chassis', 'Driveshaft', 'Wheel', 'Wheel',
                     'Wheel', 'Wheel', 'Hub', 'Tire', 'Lug Nut', 'Cylinder',
                     'Cylinder', 'Cylinder', 'Cylinder', 'Drive Output',
                     'Mount']
        }
        self.evaluator.df = pd.DataFrame(data=data_dict)

    def test_rename_df_columns(self):
        # just need to test that the columns are as expected.
        # utils tests the two auxillary functions that rename df entries.
        expected_cols = ['Composite Thing',
                         'component',
                         'Atomic Thing',
                         ]
        self.evaluator.rename_df_columns()
        self.assertListEqual(expected_cols, list(self.evaluator.df.columns))
        self.assertEqual(set(), self.evaluator.root_node_attr_columns)

    def test_add_missing_columns(self):
        # TODO: explicitly check that the new columns are made.
        # TODO: remove reliance on excelfile data.
        # TODO: This is an incomplete test because it does not test for
        # the case of no space column to be created.
        evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            translator=self.translator)
        data_dict = {
            'Composite Thing': ['Car', 'Wheel', 'Engine'],
            'component': ['chassis', 'tire', 'mount'],
            'Atomic Thing': ['Chassis', 'Tire', 'Mount']
        }
        df = pd.DataFrame(data=data_dict)
        evaluator.df = df
        evaluator.rename_df_columns()
        expected_cols = {'Composite Thing',
                         'component',
                         'Atomic Thing',
                         'composite owner',
                         'A_composite owner_component'}
        evaluator.add_missing_columns()
        self.assertSetEqual(expected_cols, set(evaluator.df.columns))

        expected_composite_owner = ['car qua chassis context',
                                    'wheel qua tire context',
                                    'engine qua mount context']
        expected_comp_owner_comp = ['A_car qua chassis context_chassis',
                                    'A_wheel qua tire context_tire',
                                    'A_engine qua mount context_mount']
        self.assertListEqual(expected_composite_owner,
                             list(evaluator.df['composite owner']))
        self.assertListEqual(expected_comp_owner_comp,
                             list(evaluator.df[
                                 'A_composite owner_component']))

    def test_to_property_di_graph(self):
        # the goal is to create a graph object.
        # networkx provides the functionality to get the data into the graph
        # the graph itself will be tested so I should just test that a graph
        # obj exists.
        self.evaluator.rename_df_columns()
        self.evaluator.add_missing_columns()
        self.evaluator.to_property_di_graph()
        self.assertTrue(self.evaluator.prop_di_graph)
        self.assertIsInstance(self.evaluator.prop_di_graph,
                              PropertyDiGraph)

        # TODO: create tests for the properties on the Evaluator class.

    def tearDown(self):
        pass


class TestMDTranslator(unittest.TestCase):

    def setUp(self):
        # TODO: Note that this relies on CompositionGraphMaster.json
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        self.translator = MDTranslator(json_data=data)

    def test_get_root_node(self):
        root_node = 'component'
        self.assertEqual(root_node, self.translator.get_root_node())

    def test_get_cols_to_nav_map(self):
        cols_to_nav = ['Component', 'Position', 'Part']
        self.assertListEqual(
            cols_to_nav, list(self.translator.get_cols_to_nav_map().keys()))

    def test_get_pattern_graph(self):
        pattern_graph = ['Composite Thing',
                         'Atomic Thing',
                         'A_composite owner_component',
                         'composite owner',
                         'component']
        self.assertListEqual(pattern_graph,
                             self.translator.get_pattern_graph())

    def test_get_pattern_graph_edges(self):
        node_pairs_list = self.translator.get_pattern_graph_edges()
        self.assertEqual(6, len(node_pairs_list))

    def test_get_edge_type(self):
        self.assertEqual('type', self.translator.get_edge_type(index=0))

    def test_get_uml_metatype(self):
        metatype = self.translator.get_uml_metatype(
            node_key='Composite Thing')
        self.assertEqual('Class', metatype)

    def test_get_uml_stereotype(self):
        stereotype = self.translator.get_uml_stereotype(
            node_key='Composite Thing'
        )
        self.assertEqual('Block', stereotype)

        stereotype_2 = self.translator.get_uml_stereotype(
            node_key='composite owner'
        )
        self.assertEqual(None, stereotype_2)

    def test_get_uml_settings(self):
        path, setting = self.translator.get_uml_settings(
            node_key='Composite Thing'
        )
        self.assertTupleEqual(('Composite Thing', None), (path, setting))

        path_comp, setting_comp = self.translator.get_uml_settings(
            node_key='component'
        )
        self.assertEqual(('aggregation', 'composite'),
                         (path_comp, setting_comp))

    def tearDown(self):
        pass
