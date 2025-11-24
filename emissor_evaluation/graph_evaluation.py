import os
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from rdflib import ConjunctiveGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from graph.brain_measures import *
from graph.graph_measures import *
from graph.ontology_measures import *
from graph.map_rdf_files import map_scenarios


class GraphEvaluator():
    def __init__(self):
        """Creates an evaluator that will use graph metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """

    def evaluate_conversation(self, scenario_folder, rdf_folder, metrics_to_plot=None):
        print(f'----------SCENARIO:{scenario_folder}, EVALUATION:graph metrics---------')

        # Read mapping of rdf log file to turn
        file = os.path.join(scenario_folder, 'turn_to_trig_file.json')
        if not os.path.exists(file):
            map_scenarios(scenario_folder, rdf_folder)
        full_df = pd.read_json(file)

        # Recreate conversation and score graph
        rdf_count = 0
        total_turns = len(full_df)
        for idx, row in full_df.iterrows():
            print(f"Processing turn {row['Turn']}/{total_turns - 1}")

            # If first row and no graph
            if idx == 0 and not row['rdf_file']:
                # Calculate metrics on empty graph
                brain_as_graph = ConjunctiveGraph()
                brain_as_netx = rdflib_to_networkx_multidigraph(brain_as_graph)
                full_df = self._calculate_metrics(brain_as_graph, brain_as_netx, full_df, idx)

            # if row has a file to rdf, process it and calculate metrics
            elif row['rdf_file']:
                for file in row['rdf_file']:
                    # Update count
                    rdf_count += 1
                    print(f"\tFound RDF, cumulative: {rdf_count}")

                    # clear brain (for computational purposes)
                    brain_as_graph = ConjunctiveGraph()

                    # Add new
                    print(f"\tAdding triples")
                    filepath = os.path.join(rdf_folder, file)
                    brain_as_graph.parse(filepath, format='trig')
                    brain_as_netx = rdflib_to_networkx_multidigraph(brain_as_graph)

                    # Calculate metrics (only when needed! otherwise copy row)
                    full_df = self._calculate_metrics(brain_as_graph, brain_as_netx, full_df, idx, metrics_to_plot)

            # copy over values from last row to avoid recomputing on an unchanged graph
            else:
                full_df = self._copy_metrics(full_df, idx)

        # Save
        evaluation_folder = os.path.join(scenario_folder, 'evaluation')
        if not os.path.exists(evaluation_folder):
            os.mkdir(evaluation_folder)
        self._save(full_df, evaluation_folder)

        if metrics_to_plot:
            self.plot_metrics_progression(metrics_to_plot, [full_df], evaluation_folder)

    @staticmethod
    def _calculate_metrics(brain_as_graph, brain_as_netx, df, idx, metrics_to_plot):
        print(f"\tCalculating graph metrics")
        metric = 'GROUP A - Total nodes'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_count_nodes(brain_as_netx)
        metric = 'GROUP A - Total edges'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_count_edges(brain_as_netx)
        metric = 'GROUP A - Average degree'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_avg_degree(brain_as_netx)
        metric = 'GROUP A - Average degree centrality'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_avg_degree_centr(brain_as_netx)
        metric = 'GROUP A - Average closeness'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_avg_closeness(brain_as_netx)
        metric = 'GROUP A - Average betweenness'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_avg_betweenness(brain_as_netx)
        metric = 'GROUP A - Average degree connectivity'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_degree_connectivity(brain_as_netx)
        metric = 'GROUP A - Average assortativity'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_assortativity(brain_as_netx)  # good
        metric = 'GROUP A - Average node connectivity'
        if metric in metrics_to_plot: 
            df.loc[idx, metric] = get_node_connectivity(brain_as_netx) \
                if get_count_nodes(brain_as_netx) > 0 else 0
        metric = 'GROUP A - Number of components'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_components(brain_as_netx)
        metric = 'GROUP A - Number of strong components'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_assortativity(brain_as_netx)
        metric = 'GROUP A - Shortest path'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_shortest_path(brain_as_netx)
        metric = 'GROUP A - Centrality entropy'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_entropy_centr(brain_as_netx)
        metric = 'GROUP A - Closeness entropy'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_entropy_clos(brain_as_netx)
        metric = 'GROUP A - Sparseness'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_sparseness(brain_as_netx) if get_count_nodes(brain_as_netx) > 0 else 0
        ####
        print(f"\tCalculating RDF graph metrics")
        metric = 'GROUP B - Total classes'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_classes(brain_as_graph)
        metric = 'GROUP B - Total properties'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_properties(brain_as_graph)
        metric = 'GROUP B - Total instances'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_instances(brain_as_graph)
        metric = 'GROUP B - Total object properties'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_properties_object(brain_as_graph)
        metric = 'GROUP B - Total data properties'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_properties_datatype(brain_as_graph)
        metric = 'GROUP B - Total equivalent class properties'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_properties_equivClass(brain_as_graph)
        metric = 'GROUP B - Total subclass properties'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_properties_subclass(brain_as_graph)
        metric = 'GROUP B - Total entities'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_entities(brain_as_graph)
        metric = 'GROUP B - Total inverse entities'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_inverse(brain_as_graph)
        metric = 'GROUP B - Ratio of inverse relations'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_ratio_inverse_relations(brain_as_graph)
        metric = 'GROUP B - Property class ratio'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_property_class_ratio(brain_as_graph)
        metric = 'GROUP B - Average population'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_avg_population(brain_as_graph)
        metric = 'GROUP B - Class property ratio'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_class_property_ratio(brain_as_graph)
        metric =  'GROUP B - Attribute richness'
        if metric in metrics_to_plot: df.loc[idx,metric] = get_attribute_richness(brain_as_graph)
        metric = 'GROUP B - Inheritance richness'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_inheritance_richness(brain_as_graph)
        metric = 'GROUP B - Relationship richness'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_relationship_richness(brain_as_graph)
        metric = 'GROUP B - Object properties ratio'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_ratio_object_properties(brain_as_graph)
        metric = 'GROUP B - Datatype properties ratio'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_ratio_datatype_properties(brain_as_graph)
        metric = 'GROUP B - Total concept assertions'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_concept_assertions(brain_as_graph)
        metric = 'GROUP B - Total role assertions'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_role_assertions(brain_as_graph)
        metric = 'GROUP B - Total general concept inclusions'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_GCI(brain_as_graph)
        metric = 'GROUP B - Total domain axioms'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_domain_axioms(brain_as_graph)
        metric = 'GROUP B - Total range axioms'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_range_axioms(brain_as_graph)
        metric = 'GROUP B - Total role inclusions'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_role_inclusion(brain_as_graph)
        metric = 'GROUP B - Total axioms'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_axioms(brain_as_graph)
        metric = 'GROUP B - Total aBox axioms'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_aBox_axioms(brain_as_graph)
        metric = 'GROUP B - Total tBox axioms'
        if metric in metrics_to_plot: df.loc[idx, metric]  = get_number_tBox_axioms(brain_as_graph)
        #####
        print(f"\tCalculating interaction metrics")
        metric = 'GROUP C - Total triples'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_triples(brain_as_graph)  # good
        metric = 'GROUP C - Total world instances'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_grasp_instances(brain_as_graph)
        metric = 'GROUP C - Total claims'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_statements(brain_as_graph)
        metric = 'GROUP C - Total perspectives'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_perspectives(brain_as_graph)
        metric = 'GROUP C - Total mentions'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_mentions(brain_as_graph)
        metric = 'GROUP C - Total conflicts'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_negation_conflicts(brain_as_graph)
        metric = 'GROUP C - Total sources'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_sources(brain_as_graph)
        metric = 'GROUP C - Total interactions'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_chats(brain_as_graph)
        metric = 'GROUP C - Total utterances'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_number_utterances(brain_as_graph)

        metric = 'GROUP C - Ratio claim to triples'
        if metric in metrics_to_plot:
            df.loc[idx, metric metric] = df.loc[idx, 'GROUP C - Total claims'] / df.loc[
                idx, 'GROUP C - Total triples']  # how much knowledge
        metric = 'GROUP C - Ratio perspectives to triples'
        if metric in metrics_to_plot: df.loc[idx, metric] = df.loc[idx, 'GROUP C - Total perspectives'] / df.loc[
            idx, 'GROUP C - Total triples']  # how much diversity of opinion
        metric = 'GROUP C - Ratio conflicts to triples'
        if metric in metrics_to_plot: df.loc[idx, metric] = df.loc[idx, 'GROUP C - Total conflicts'] / df.loc[
            idx, 'GROUP C - Total triples']  # how much conflicting info
        metric = 'GROUP C - Ratio perspectives to claims'
        if metric in metrics_to_plot: df.loc[idx, metric] = df.loc[idx, 'GROUP C - Total perspectives'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of opinions
        metric = 'GROUP C - Ratio mentions to claims'
        if metric in metrics_to_plot: df.loc[idx, metric] = df.loc[idx, 'GROUP C - Total mentions'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of mentions
        metric = 'GROUP C - Ratio conflicts to claims'
        if metric in metrics_to_plot: df.loc[idx, metric] = df.loc[idx, 'GROUP C - Total conflicts'] / df.loc[
            idx, 'GROUP C - Total claims'] if df.loc[idx, 'GROUP C - Total claims'] != 0 else 0  # density of conflicts

        metric = 'GROUP C - Average perspectives per claim'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_average_views_per_factoid(brain_as_graph)
        metric = 'GROUP C - Average mentions per claim'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_average_mentions_per_factoid(brain_as_graph)
        metric = 'GROUP C - Average turns per interaction'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_average_turns_per_interaction(brain_as_graph)
        metric = 'GROUP C - Average claims per source'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_average_factoids_per_source(brain_as_graph)
        metric = 'GROUP C - Average perspectives per source'
        if metric in metrics_to_plot: df.loc[idx, metric] = get_average_views_per_source(brain_as_graph)
        return df

    @staticmethod
    def _copy_metrics(df, idx):
        existing_columns = df.columns
        group_a = ['GROUP A - Total nodes', 'GROUP A - Total edges', 'GROUP A - Average degree',
                   'GROUP A - Average degree centrality', 'GROUP A - Average closeness',
                   'GROUP A - Average betweenness',
                   'GROUP A - Average degree connectivity', 'GROUP A - Average assortativity',
                   'GROUP A - Average node connectivity', 'GROUP A - Number of components',
                   'GROUP A - Number of strong components', 'GROUP A - Shortest path', 'GROUP A - Centrality entropy',
                   'GROUP A - Closeness entropy', 'GROUP A - Sparseness']

        group_b = ['GROUP B - Total classes', 'GROUP B - Total properties', 'GROUP B - Total instances',
                   'GROUP B - Total object properties', 'GROUP B - Total data properties',
                   'GROUP B - Total equivalent class properties', 'GROUP B - Total subclass properties',
                   'GROUP B - Total inverse entities', 'GROUP B - Ratio of inverse relations',
                   'GROUP B - Property class ratio', 'GROUP B - Average population', 'GROUP B - Class property ratio',
                   'GROUP B - Attribute richness', 'GROUP B - Inheritance richness', 'GROUP B - Relationship richness',
                   'GROUP B - Object properties ratio', 'GROUP B - Datatype properties ratio',
                   'GROUP B - Total role assertions', 'GROUP B - Total general concept inclusions',
                   'GROUP B - Total domain axioms', 'GROUP B - Total range axioms', 'GROUP B - Total role inclusions',
                   'GROUP B - Total axioms', 'GROUP B - Total aBox axioms', 'GROUP B - Total tBox axioms'
                   ]

        group_c = ['GROUP C - Total triples', 'GROUP C - Total world instances', 'GROUP C - Total claims',
                   'GROUP C - Total perspectives', 'GROUP C - Total mentions', 'GROUP C - Total conflicts',
                   'GROUP C - Total sources', 'GROUP C - Total interactions', 'GROUP C - Total utterances',
                   'GROUP C - Ratio claim to triples', 'GROUP C - Ratio perspectives to triples',
                   'GROUP C - Ratio conflicts to triples', 'GROUP C - Ratio perspectives to claims',
                   'GROUP C - Ratio mentions to claims', 'GROUP C - Ratio conflicts to claims',
                   'GROUP C - Average perspectives per claim', 'GROUP C - Average mentions per claim',
                   'GROUP C - Average turns per interaction', 'GROUP C - Average claims per source',
                   'GROUP C - Average perspectives per source'
                   ]

        print(f"\tCopying graph metrics")
        for metric in group_a + group_b + group_c:
            if metric in existing_columns:
                df.loc[idx, metric] = df.loc[idx - 1, metric]

        return df

    @staticmethod
    def _save(df, evaluation_folder):
        #df = df.drop(columns=['Speaker', 'Response', 'rdf_file'])
        file = os.path.join(evaluation_folder, 'graph_evaluation2.csv')
        df.to_csv(file, sep=";", index=False)
        print(f"\n\tSaved to file: {file}")

    def plot_metrics_progression(self, metrics, convo_dfs, evaluation_folder):
        # Plot metrics progression per conversation
        for metric in metrics:
            metric_df = pd.DataFrame()

            # Iterate conversations
            for idx, convo_df in enumerate(convo_dfs):
                conversation_id = f'Conversation {idx}'
                convo_df = convo_df.set_index('Turn')

                # Add into a dataframe
                if len(metric_df) == 0:
                    metric_df[conversation_id] = convo_df[metric]
                else:
                    metric_df = pd.concat([metric_df, convo_df[metric]], axis=1)
                    metric_df.rename(columns={metric: conversation_id}, inplace=True)

            # Cutoff and plot
            self.plot_progression(metric_df, metric, evaluation_folder)

    @staticmethod
    def plot_progression(df_to_plot, xlabel, evaluation_folder):
        df_to_plot = df_to_plot.reset_index().melt('Turn', var_name='cols', value_name=xlabel)

        g = sns.relplot(x="Turn", y=xlabel, hue='cols', data=df_to_plot, kind='line')

        ax = plt.gca()
        plt.xlim(0)
        plt.xticks(ax.get_xticks()[::5], rotation=45)

        plot_file = os.path.join(evaluation_folder, f"{xlabel}.png")
        g.figure.savefig(plot_file, dpi=300, transparent=True, bbox_inches='tight')
        plt.close()
        print(f"\tSaved to file: {plot_file}")



def main(emissor_path:str, scenario:str):
    metrics=['GROUP A - Average degree', 
        'GROUP A - Sparseness', 
        #'GROUP A - Shortest path',
        #'GROUP A - Number of components', 
        'GROUP A - Centrality entropy',
        #'GROUP B - Average population',
        'GROUP C - Total triples', 
        'GROUP C - Total world instances',
        'GROUP C - Total claims',
        'GROUP C - Total perspectives', 
        'GROUP C - Total mentions',
        #'GROUP C - Total conflicts',
        'GROUP C - Total sources', 
        #'GROUP C - Total interactions',
        #'GROUP C - Total utterances',
        'GROUP C - Ratio claim to triples', 
        #'GROUP C - Ratio perspectives to triples',
        #'GROUP C - Ratio conflicts to triples', 
        #'GROUP C - Ratio perspectives to claims',
        #'GROUP C - Ratio mentions to claims', 
        #'GROUP C - Ratio conflicts to claims',
        #'GROUP C - Average perspectives per claim', 
        #'GROUP C - Average mentions per claim',
        #'GROUP C - Average turns per interaction', 
        #'GROUP C - Average claims per source',
        #'GROUP C - Average perspectives per source'
            ]
    scenario_path = os.path.join(emissor_path, scenario)
    print(type(scenario_path))
    rdf = os.path.join(scenario_path, "rdf")
    if os.path.exists(rdf):
        evaluator = GraphEvaluator()
        rdf_path = Path(rdf)
        evaluator.evaluate_conversation(scenario_path, rdf_folder=rdf_path, metrics_to_plot = metrics)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor-path', type=str, required=False, help="Path to the emissor folder", default='')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)

    main(args.emissor_path, args.scenario)

