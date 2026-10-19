import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Columns that identify or number a turn and should not be plotted as a metric
NON_METRIC_COLUMNS = ['Turn', 'Turn nr.']
# Separates the line label from the speaker in the column names of the dataframes that are plotted
SPEAKER_SEPARATOR = ' | '


class Plotter():
    def __init__(self):
        """Creates a plotter that shows the progression of evaluation metrics across the turns of conversations.
        params
        returns: None
        """
        super(Plotter, self).__init__()

    @staticmethod
    def find_metric_files(scenarios_path, metric):
        """Returns all csv files in the 'evaluation' subfolder of each scenario that have the metric as a substring in the filename."""
        scenarios_paths = sorted([path for path in scenarios_path.iterdir()
                                  if path.is_dir() and path.stem not in ['.idea', 'plots']])
        metric_files = []
        for scenario in scenarios_paths:
            evaluation_folder = scenario / 'evaluation'
            if not evaluation_folder.is_dir():
                continue
            for file in sorted(evaluation_folder.glob('*.csv')):
                if metric in file.name:
                    metric_files.append((scenario, file))
        return metric_files

    @staticmethod
    def get_turn_order(scenarios_path, scenario_id):
        """Returns a dictionary from turn identifier to turn number in the order of the conversation in the EMISSOR scenario,
        or None if the scenario cannot be loaded."""
        try:
            from src.cltl.emissor_evaluation.emissor import emissor_util as util
            text_signals = util.get_text_signals_from_a_scenario(str(scenarios_path), scenario_id)
        except Exception as e:
            print(f"Could not load the turns of scenario {scenario_id}, using the row order of the csv files: {e}")
            return None
        return {text_signal.id: index for index, text_signal in enumerate(text_signals)}

    @staticmethod
    def set_turn_numbers(convo_df, turn_order):
        """Indexes the rows by turn number. Rows without a turn identifier, such as AVERAGE rows, are removed.
        The turn number is taken from the conversation order in the scenario, so that files that were sorted
        (e.g. by speaker) are still plotted in the order of the conversation. Otherwise the row order is used."""
        if 'Turn' in convo_df.columns:
            convo_df = convo_df[convo_df['Turn'].notna()]
            if turn_order and convo_df['Turn'].isin(turn_order.keys()).all():
                convo_df = convo_df.set_index(convo_df['Turn'].map(turn_order).rename(None)).sort_index()
            else:
                convo_df = convo_df.reset_index(drop=True)
        convo_df.index.name = 'Turn'
        return convo_df

    @staticmethod
    def read_evaluation_file(file):
        """Reads an evaluation csv file. The files saved by the notebooks use ';' as separator."""
        df = pd.read_csv(file, sep=';', header=0)
        if len(df.columns) == 1:
            df = pd.read_csv(file, sep=',', header=0)
        return df

    @staticmethod
    def split_by_speaker(convo_df, values, label):
        """Splits the values of a column into a separate series for each speaker, so that each speaker gets its own line."""
        if 'Speaker' not in convo_df.columns:
            return [values.rename(label)]
        series = []
        for speaker in convo_df['Speaker'].dropna().unique():
            speaker_values = values[convo_df['Speaker'] == speaker]
            if not speaker_values.dropna().empty:
                series.append(speaker_values.rename(f"{label}{SPEAKER_SEPARATOR}{speaker}"))
        return series

    def plot_conversations(self, scenarios_path, metrics, columns=None):
        """Plots the metric columns of all csv files that match the metrics, with one line per conversation.
        params
        scenarios_path: folder with the EMISSOR scenarios
        metrics: list of substrings to match against the csv filenames, e.g. ['likelihood', 'llm_judge']
        columns: optional list of columns to plot, by default all numeric columns are plotted
        returns: None
        """
        scenarios_path = Path(scenarios_path)
        plots_folder = scenarios_path / 'plots'
        plots_folder.mkdir(exist_ok=True)

        for metric in metrics:
            metric_files = self.find_metric_files(scenarios_path, metric)
            if not metric_files:
                print(f"No csv files found with '{metric}' in the filename")
                continue

            # Collect each numeric column per conversation, indexed by turn number
            column_dfs = {}
            turn_orders = {}
            for scenario, file in metric_files:
                try:
                    convo_df = self.read_evaluation_file(file)
                except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                    print(f"Skipping {file}, it could not be read: {e}")
                    continue
                if scenario.stem not in turn_orders:
                    turn_orders[scenario.stem] = self.get_turn_order(scenarios_path, scenario.stem)
                convo_df = self.set_turn_numbers(convo_df, turn_orders[scenario.stem])
                # Label with the scenario and the part of the filename after the scenario id,
                # so that different files of the same scenario can be told apart
                conversation_id = f"{scenario.stem} {file.stem.replace(scenario.stem, '').strip('_')}"

                numeric_columns = [column for column in convo_df.select_dtypes('number').columns
                                   if column not in NON_METRIC_COLUMNS]
                if columns:
                    numeric_columns = [column for column in numeric_columns if column in columns]
                for column in numeric_columns:
                    column_dfs.setdefault(column, []).extend(self.split_by_speaker(convo_df, convo_df[column], conversation_id))

            # Plot
            for column, series in column_dfs.items():
                metric_df = pd.concat(series, axis=1)
                if metric_df.dropna(how='all').empty:
                    print(f"Skipping '{column}' for '{metric}', it has no values")
                    continue
                self.plot_progression(metric_df, column, plots_folder, f"{metric}_{column}")

    def plot_scenario(self, scenarios_path, scenario_id, metrics, columns=None, normalize=False):
        """Plots the metric columns of all csv files of a single scenario that match the metrics in one plot,
        with one line per metric column.
        params
        scenarios_path: folder with the EMISSOR scenarios
        scenario_id: the scenario to plot
        metrics: list of substrings to match against the csv filenames, e.g. ['likelihood', 'llm_judge']
        columns: optional list of columns to plot, by default all numeric columns are plotted
        normalize: scale each line to the range 0-1, useful when metrics have different scales such as graph counts
        returns: None
        """
        scenario = Path(scenarios_path) / scenario_id
        evaluation_folder = scenario / 'evaluation'
        if not evaluation_folder.is_dir():
            print(f"No evaluation folder found for scenario {scenario_id}")
            return

        # Collect each numeric column of each matching file, indexed by turn number
        turn_order = self.get_turn_order(scenarios_path, scenario_id)
        series = []
        for file in sorted(evaluation_folder.glob('*.csv')):
            matching_metrics = [metric for metric in metrics if metric in file.name]
            if not matching_metrics:
                continue
            try:
                convo_df = self.read_evaluation_file(file)
            except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                print(f"Skipping {file}, it could not be read: {e}")
                continue
            convo_df = self.set_turn_numbers(convo_df, turn_order)
            # Label with the part of the filename after the scenario id and the column
            file_label = file.stem.replace(scenario_id, '').strip('_')

            numeric_columns = [column for column in convo_df.select_dtypes('number').columns
                               if column not in NON_METRIC_COLUMNS]
            if columns:
                numeric_columns = [column for column in numeric_columns if column in columns]
            for column in numeric_columns:
                values = convo_df[column]
                if values.dropna().empty:
                    continue
                if normalize:
                    value_range = values.max() - values.min()
                    values = (values - values.min()) / value_range if value_range else values * 0
                series.extend(self.split_by_speaker(convo_df, values, f"{file_label} {column}"))

        if not series:
            print(f"No values found for {metrics} in scenario {scenario_id}")
            return

        # Plot
        ylabel = 'Normalized score' if normalize else 'Score'
        plot_name = f"{scenario_id}_{'_'.join(metrics)}_combined"
        self.plot_progression(pd.concat(series, axis=1), ylabel, evaluation_folder, plot_name, legend_title='Metric')

    @staticmethod
    def plot_progression(df_to_plot, ylabel, plots_folder, plot_name, legend_title='Conversation'):
        # Re-structure
        df_to_plot = df_to_plot.reset_index().melt('Turn', var_name=legend_title, value_name=ylabel)
        df_to_plot = df_to_plot.dropna(subset=[ylabel])

        # Plot, with a separate plot next to each other for each speaker if the lines are split by speaker
        col = None
        col_order = None
        if df_to_plot[legend_title].str.contains(SPEAKER_SEPARATOR, regex=False).any():
            labels = df_to_plot[legend_title].str.split(SPEAKER_SEPARATOR, n=1, regex=False)
            df_to_plot[legend_title] = labels.str[0]
            df_to_plot['Speaker'] = labels.str[1].fillna('')
            col = 'Speaker'
            col_order = sorted(df_to_plot['Speaker'].unique())
        g = sns.relplot(x="Turn", y=ylabel, hue=legend_title, col=col, col_order=col_order,
                        data=df_to_plot, kind='line')
        if col:
            g.set_titles("{col_name}")
        g.set(xlim=(0, None))
        g.tick_params(axis='x', rotation=45)

        # Save
        safe_name = "".join(char if char.isalnum() or char in '-_.' else '_' for char in plot_name)
        plot_file = plots_folder / f"{safe_name}.png"
        print(plot_file)
        g.figure.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close(g.figure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation metrics of EMISSOR scenarios across turns.')
    parser.add_argument('scenarios_path', help='Folder with the EMISSOR scenarios')
    parser.add_argument('metrics', nargs='+', help="Substrings to match in the csv filenames, e.g. likelihood llm_judge")
    parser.add_argument('--columns', nargs='+', help='Only plot these columns')
    parser.add_argument('--scenario', help='Combine the metrics of this scenario in a single plot')
    parser.add_argument('--normalize', action='store_true', help='Scale each line to 0-1 in the combined plot')
    args = parser.parse_args()

    if args.scenario:
        Plotter().plot_scenario(args.scenarios_path, args.scenario, args.metrics, args.columns, args.normalize)
    else:
        Plotter().plot_conversations(args.scenarios_path, args.metrics, args.columns)
