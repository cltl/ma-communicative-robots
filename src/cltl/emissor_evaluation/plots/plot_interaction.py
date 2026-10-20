import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
import sys
import base64
from emissor.representation.scenario import Signal
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
from src.cltl.emissor_evaluation.emissor import text_signal as text_signal_util
from src.cltl.emissor_evaluation.emissor import image_signal as image_signal_util
from src.cltl.emissor_evaluation.emissor import scenario_check as check

class PlotSettings():
    _LLH_THRESHOLD = 0
    _SENTIMENT_THRESHOLD = 0
    _ANNOTATIONS =[]
    _START = 0
    _END = -1

## TEXT ONLY
def get_signal_rows(signals:[Signal], human, agent, settings: PlotSettings):
    data = []
    print('Nr of signals', len(signals))
    for i, signal in enumerate(signals):
        if i>= settings._START and (i<= settings._END or settings._END==-1):
            speaker = text_signal_util.get_speaker_from_text_signal(signal)
            if speaker.lower()=='speaker':
                speaker = human
            elif speaker.lower()=='agent':
                speaker = agent
            text = ''.join(signal.seq)
            score = 0
            score += text_signal_util.get_dact_feedback_score_from_text_signal(signal)
            if "sentiment" in settings._ANNOTATIONS:
                score += text_signal_util.get_sentiment_score_from_text_signal(signal)
            if "ekman" in settings._ANNOTATIONS:
                score += text_signal_util.get_ekman_feedback_score_from_text_signal(signal)
            if "go" in settings._ANNOTATIONS:
                score += text_signal_util.get_go_feedback_score_from_text_signal(signal)
            if "llh" in settings._ANNOTATIONS:
                score += text_signal_util.get_likelihood_from_text_signal(signal, settings._LLH_THRESHOLD)

            label = text_signal_util.make_annotation_label(signal, settings._SENTIMENT_THRESHOLD, settings._ANNOTATIONS)
            row = {'turn':i+1, 'utterance': text, 'score': score, "speaker": speaker, "type":signal.modality, "annotation": label}
            data.append(row)
    return data

def get_multimodal_signals(emissor_path, scenario):
    signalDict = {}
    sorted_signal_list = []
    scenario_storage = ScenarioStorage(emissor_path)
    scenario_ctrl = scenario_storage.load_scenario(scenario)
    text_signals = []
    try:
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    except:
        print('Could not extract text signals from text.json')
    image_signals = []
    try:
        image_signals =  scenario_ctrl.get_signals(Modality.IMAGE)
    except:
        print('Could not extract image signals from image.json')
    for signal in text_signals+image_signals:
        time = signal.time.start
        if time in signalDict:
            signalDict[time].append(signal)
        else:
            signalDict[time] = [signal]

    times = list(signalDict.keys())
    times.sort()
    for time in times:
        signals = signalDict[time]
        for signal in signals:
            sorted_signal_list.append(signal)
    return sorted_signal_list

def get_multimodal_signal_rows(signals:[Signal], human, agent, settings: PlotSettings):
    data = []
    print('Nr of signals', len(signals))
    previous_image_label = ""
    previous_image_id = ""
    last_image_turn = 0
    margin = 0
    last_signal_type = None
    for i, signal in enumerate(signals):
        if i>= settings._START and (i<= settings._END or settings._END==-1):
            if signal.modality==Modality.TEXT:
                speaker = text_signal_util.get_speaker_from_text_signal(signal)
                if speaker.lower() == 'speaker':
                    speaker = human
                elif speaker.lower() == 'agent':
                    speaker = agent
                text = ''.join(signal.seq)
                score = 0
                if "dialog_act" in settings._ANNOTATIONS:
                    score += text_signal_util.get_dact_feedback_score_from_text_signal(signal)
                if "sentiment" in settings._ANNOTATIONS:
                    score += text_signal_util.get_sentiment_score_from_text_signal(signal)
                if "ekman" in settings._ANNOTATIONS:
                    score += text_signal_util.get_ekman_feedback_score_from_text_signal(signal)
                if "go" in settings._ANNOTATIONS:
                    score += text_signal_util.get_go_feedback_score_from_text_signal(signal)
                if "llh" in settings._ANNOTATIONS:
                    score += text_signal_util.get_likelihood_from_text_signal(signal, settings._LLH_THRESHOLD)

                label = text_signal_util.make_annotation_label(signal, settings._SENTIMENT_THRESHOLD, settings._ANNOTATIONS)
                row = {'turn':i+margin, 'utterance': text, 'score': score, "speaker": speaker, "type":signal.modality, "annotation": label}
                data.append(row)
                last_signal_type = Modality.TEXT
            elif signal.modality==Modality.IMAGE:
                score = 0
                score += image_signal_util.get_emotic_feedback_score_from_signal(signal)
                object, face, id, emotion = image_signal_util.make_annotation_label(signal)
                object_type = object
                row = None
                if "-" in object:
                    object_type = object[:object.index("-")]
                if not id == previous_image_id and last_signal_type==Modality.TEXT:
                    row = {'turn':i+margin, 'utterance': id[:5], 'score': score, "speaker": "camera", "type":signal.modality, "annotation": face+";"+emotion+";"+object}
                elif not object_type==previous_image_label and last_signal_type==Modality.TEXT:
                    row = {'turn':i+margin, 'utterance': id[:5], 'score': score, "speaker": "camera", "type":signal.modality, "annotation": face+";"+emotion+";"+object}
                elif i+margin>last_image_turn and last_signal_type== Modality.TEXT:
                        print(i+margin, last_image_turn)
                        print(id)
                        print(object_type)
                        row = {'turn':i+margin, 'utterance': id[:5], 'score': score, "speaker": "camera", "type":signal.modality, "annotation": emotion}
                previous_image_label = object_type
                previous_image_id = id
                last_image_turn = i+margin
                last_signal_type = Modality.IMAGE
                if row:
                    data.append(row)
    return data


def create_timeline_image(emissor_path, scenario, settings: PlotSettings):
    scenario_storage = ScenarioStorage(emissor_path)
    scenario_ctrl = scenario_storage.load_scenario(scenario)
    speaker = "No speaker"
    agent = "No agent"
    try:
        speaker = scenario_ctrl.scenario.context.speaker["name"] if "name" in scenario_ctrl.scenario.context.speaker else "No speaker"
    except:
        print("No speaker name in context")
    try:
        agent = scenario_ctrl.scenario.context.agent["name"] if "name" in scenario_ctrl.scenario.context.agent else "No agent"
    except:
        print("No agent name in context")
    signals = get_multimodal_signals(emissor_path, scenario)
    rows = get_multimodal_signal_rows(signals, speaker, agent, settings)

    evaluation_folder = os.path.join(emissor_path, scenario, "evaluation")
    if not os.path.exists(evaluation_folder):
        os.mkdir(evaluation_folder)
    name= scenario
    if settings._START>0:
        name += "_S"+ str(settings._START)
    if settings._END>-1:
        name += "_E"+str(settings._END)
    path = os.path.join(evaluation_folder, name+"_plot.png")
    draw_timeline(rows, path)


# Size of the timeline plots: the width grows with the number of turns, the text of the turns goes below the plot
TURN_WIDTH = 2.5
PLOT_HEIGHT = 8
# Height in pixels of the plot shown in a notebook, the plot can be scrolled horizontally
DISPLAY_HEIGHT = 800

def set_plot_style():
   # sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})  ## grey background
    sns.set_style("whitegrid", {"grid.color": ".8", "grid.linestyle": ":", 'axes.grid': True})
    sns.set_context("talk", font_scale=0.9)
    ### other themes: paper, talk, poster, notebook (default)

def draw_timeline(rows, path, ylim=(-5, 5)):
    set_plot_style()
    fig, ax = plt.subplots(figsize=(max(10, TURN_WIDTH*len(rows)), PLOT_HEIGHT))
    draw_timeline_on_axis(ax, rows, ylim)

   # plt.savefig(path, dpi=600)
    # bbox_inches='tight' keeps the labels that stick out above the plot
    fig.savefig(path, bbox_inches='tight')
    print('Saved plot to', path)
    plt.close(fig)
    show_scrollable(path)

def get_point_label(row):
    """The label of a data point: the annotation with the score, three annotations per line."""
    annotations = [annotation for annotation in row['annotation'].split(";") if annotation]
    return "\n".join(";".join(annotations[i:i+3]) for i in range(0, len(annotations), 3))

def draw_timeline_on_axis(ax, rows, ylim=(-5, 5)):
    df = pd.DataFrame(rows)
    ax = sns.lineplot(x='turn', y='score', data=df, hue='speaker', style='speaker', markers=True, palette="deep",
                      linewidth=2.5, markersize=12, legend="brief", ax=ax)
    #palette = "pastel, flare/bright/deep/muted/colorblind/dark"
    for index, row in df.iterrows():
            if row['speaker']:
                x = row['turn']
                y = row['score']
                category = get_point_label(row)
                signalType = row['type']
                if signalType==Modality.TEXT:
                    ax.annotate(category, (x, y), xytext=(8, 8), textcoords='offset points',
                                horizontalalignment='left', size='small', color='black', verticalalignment='bottom',
                                linespacing=1.3, bbox=LABEL_BOX, rotation=POINT_LABEL_ROTATION, rotation_mode='anchor')
                elif signalType==Modality.IMAGE:
                    ax.annotate(category, (x, y), xytext=(-8, -8), textcoords='offset points',
                                horizontalalignment='right', size='small', color='blue', verticalalignment='top',
                                linespacing=1.3, bbox=LABEL_BOX, rotation=POINT_LABEL_ROTATION, rotation_mode='anchor')

    # the text of every turn on the x-axis
    set_turn_labels(ax, {row['turn']: get_turn_label(row) for _, row in df.iterrows()})
    ax.legend(loc='lower right', frameon=True)
    if ylim:
        # widen the range if scores fall outside it, so that no turn is cut off
        ax.set_ylim(min(ylim[0], df['score'].min() - 1), max(ylim[1], df['score'].max() + 1))

# Angle of the labels of the data points, so that labels of neighbouring turns do not overlap
POINT_LABEL_ROTATION = 45

# White background behind the labels so that they stay readable when they cross lines or other labels
LABEL_BOX = dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2)

def show_scrollable(path, height=DISPLAY_HEIGHT):
    """Shows the saved plot in a notebook with a fixed height and a horizontal scrollbar, instead of shrinking it to the
    width of the notebook. Does nothing when not running in a notebook."""
    try:
        from IPython import get_ipython
        from IPython.display import HTML, display
        if get_ipython() is None or not hasattr(get_ipython(), 'kernel'):
            return
    except ImportError:
        return
    with open(path, 'rb') as image_file:
        data = base64.b64encode(image_file.read()).decode('ascii')
    display(HTML(f'<div style="overflow-x:auto; width:100%;">'
                 f'<img src="data:image/png;base64,{data}" style="height:{height}px; max-width:none;"></div>'))


## CSV
def get_csv_rows(csv_file, score_column, settings: PlotSettings, turn_order=None,
                 turn_column='Turn', speaker_column='Speaker', text_column='Response', label_column=None):
    """Creates the rows for the timeline from a csv file with a column for the turn id, the speaker, the turn and the score,
    such as the evaluation files saved by the notebooks in emissor_evaluation.
    Rows without a turn id, such as AVERAGE rows, are skipped. If turn_order (turn id -> position) is given,
    the rows are sorted in the order of the conversation, otherwise the order of the csv file is used.
    If label_column is given, its value is added to the label of each data point, e.g. the dialogue act."""
    df = read_csv(csv_file)
    for column in [turn_column, speaker_column, text_column, score_column] + ([label_column] if label_column else []):
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in {csv_file}, the columns are: {list(df.columns)}")
    df = df[df[turn_column].notna()]
    use_turn_order = turn_order and df[turn_column].isin(turn_order.keys()).all()
    if use_turn_order:
        df = df.assign(_order=df[turn_column].map(turn_order)).sort_values('_order')
    print('Nr of turns', len(df))

    data = []
    for i, (_, csv_row) in enumerate(df.iterrows()):
        # with the turn order, the turn number is the position in the conversation, so that plots of different
        # csv files of the same scenario line up even if a file misses some turns
        if use_turn_order:
            i = csv_row['_order']
        if i>= settings._START and (i<= settings._END or settings._END==-1):
            score = csv_row[score_column]
            score = 0 if pd.isna(score) else float(score)
            text = "" if pd.isna(csv_row[text_column]) else str(csv_row[text_column])
            annotation = f"{score_column}={score:.2f}"
            if label_column and not pd.isna(csv_row[label_column]):
                # the label on the first line and the score below it
                annotation = f"{csv_row[label_column]}\n{annotation}"
            row = {'turn':i+1, 'utterance': text, 'score': score, "speaker": str(csv_row[speaker_column]),
                   "type":Modality.TEXT, "annotation": annotation}
            data.append(row)
    return data

def read_csv(csv_file):
    """Reads a csv file, the evaluation files saved by the notebooks use ';' as separator."""
    df = pd.read_csv(csv_file, sep=';')
    if len(df.columns) == 1:
        df = pd.read_csv(csv_file, sep=',')
    return df

def get_csv_ylim(rows):
    """The scores in csv files have their own range, so the y-axis follows the data with some room for the labels."""
    scores = [row['score'] for row in rows]
    margin = max(max(scores) - min(scores), 1) * 0.5
    return min(scores) - margin, max(scores) + margin

def get_turn_order(emissor_path, scenario):
    """Returns a dictionary from text signal id to its position in the conversation of the scenario."""
    scenario_storage = ScenarioStorage(emissor_path)
    scenario_ctrl = scenario_storage.load_scenario(scenario)
    text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    return {signal.id: index for index, signal in enumerate(text_signals)}

def create_timeline_image_from_csv(csv_file, score_column, settings: PlotSettings, emissor_path=None, scenario=None,
                                   turn_column='Turn', speaker_column='Speaker', text_column='Response',
                                   label_column=None):
    """Plots the interaction as a timeline with the scores from a column in a csv file.
    If emissor_path and scenario are given, the turns are put in the order of the conversation in the scenario,
    which is needed when the csv file was sorted, e.g. by speaker.
    label_column: optional column whose value is added to the score in the label of each data point,
                  e.g. 'dialogue_act' for the dialogue act files or 'go_emotion' for the emotion files.
                  None for scores without such a value, such as likelihood and coherence.
    The plot is saved next to the csv file and the path of the plot is returned."""
    turn_order = None
    if emissor_path and scenario:
        try:
            turn_order = get_turn_order(emissor_path, scenario)
        except Exception as e:
            print('Could not load the turns of the scenario, using the order of the csv file:', e)
    rows = get_csv_rows(csv_file, score_column, settings, turn_order, turn_column, speaker_column, text_column,
                        label_column)
    if not rows:
        print('No turns to plot in', csv_file)
        return

    name = os.path.splitext(os.path.basename(csv_file))[0] + "_" + score_column
    if settings._START>0:
        name += "_S"+ str(settings._START)
    if settings._END>-1:
        name += "_E"+str(settings._END)
    path = os.path.join(os.path.dirname(os.path.abspath(csv_file)), name+"_plot.png")
    draw_timeline(rows, path, ylim=get_csv_ylim(rows))
    return path

# Score columns of the evaluation files saved by the notebooks in emissor_evaluation, other files use their first score column
DEFAULT_SCORES = {'likelihood': 'llh', 'llm_judge': 'llm_coherence', 'emotion': 'emotion_score', 'dialogue_act': 'da_score'}

def get_score_column(df, csv_file, scores, columns):
    """Returns the score column to plot for a csv file: the column given in scores for a substring of the filename,
    otherwise the first numeric column with values that is not one of the given columns."""
    file_name = os.path.basename(csv_file)
    for substring, score_column in scores.items():
        if substring in file_name and score_column in df.columns:
            return score_column
    for column in df.select_dtypes('number').columns:
        if column not in columns and column != 'Turn nr.' and df[column].notna().any():
            return column
    return None

def get_csv_plots(emissor_path, scenario, settings: PlotSettings, metrics=None, scores=None,
                  turn_column='Turn', speaker_column='Speaker', text_column='Response'):
    """Returns a list of (name, score column, rows) for each csv file in the evaluation folder of a scenario
    that matches the metrics, with the rows in the order of the conversation."""
    evaluation_folder = os.path.join(emissor_path, scenario, "evaluation")
    scores = {**DEFAULT_SCORES, **(scores or {})}
    turn_order = None
    try:
        turn_order = get_turn_order(emissor_path, scenario)
    except Exception as e:
        print('Could not load the turns of the scenario, using the order of the csv files:', e)

    plots = []
    for file_name in sorted(os.listdir(evaluation_folder)):
        if not file_name.endswith('.csv') or (metrics and not any(metric in file_name for metric in metrics)):
            continue
        csv_file = os.path.join(evaluation_folder, file_name)
        try:
            df = read_csv(csv_file)
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            print('Skipping', file_name, 'it could not be read:', e)
            continue
        if not all(column in df.columns for column in [turn_column, speaker_column, text_column]):
            print('Skipping', file_name, 'it has no', [turn_column, speaker_column, text_column], 'columns')
            continue
        score_column = get_score_column(df, csv_file, scores, [turn_column, speaker_column, text_column])
        if not score_column:
            print('Skipping', file_name, 'it has no score column with values')
            continue
        rows = get_csv_rows(csv_file, score_column, settings, turn_order, turn_column, speaker_column, text_column)
        if rows:
            plots.append((file_name.replace(scenario, '').strip('_').replace('.csv', ''), score_column, rows))

    return plots

def create_stacked_timeline_image_from_csvs(emissor_path, scenario, settings: PlotSettings, metrics=None, scores=None,
                                            turn_column='Turn', speaker_column='Speaker', text_column='Response'):
    """Plots the timelines of all csv files in the evaluation folder of a scenario as aligned plots under each other
    in a single image, with the same turn numbers on the x-axis.
    metrics: optional list of substrings, only csv files with one of them in the filename are plotted
    scores: optional dictionary from a substring of the filename to the score column to plot, e.g. {'manual': 'Coherent'},
            added to DEFAULT_SCORES; for other files the first numeric column is plotted
    The image is saved in the evaluation folder as <scenario>_stacked_plot.png and its path is returned."""
    evaluation_folder = os.path.join(emissor_path, scenario, "evaluation")
    plots = get_csv_plots(emissor_path, scenario, settings, metrics, scores, turn_column, speaker_column, text_column)
    if not plots:
        print('No csv files to plot in', evaluation_folder)
        return

    set_plot_style()
    nr_of_turns = max(row['turn'] for _, _, rows in plots for row in rows)
    fig, axes = plt.subplots(len(plots), 1, squeeze=False,
                             figsize=(max(10, TURN_WIDTH*nr_of_turns), PLOT_HEIGHT*len(plots)))
    # the turns of all csv files under every plot, so that the plots line up even if a file misses some turns
    turn_labels = {row['turn']: get_turn_label(row) for _, _, rows in plots for row in rows}
    for ax, (name, score_column, rows) in zip(axes[:, 0], plots):
        draw_timeline_on_axis(ax, rows, ylim=get_csv_ylim(rows))
        set_turn_labels(ax, turn_labels)
        ax.set_title(f"{name}: {score_column}", loc='left', fontweight='bold')
        ax.set_ylabel(score_column)

    name = scenario + "_stacked"
    if settings._START>0:
        name += "_S"+ str(settings._START)
    if settings._END>-1:
        name += "_E"+str(settings._END)
    path = os.path.join(evaluation_folder, name + "_plot.png")
    fig.subplots_adjust(hspace=0.9)
    fig.savefig(path, bbox_inches='tight')
    print('Saved plot to', path)
    plt.close(fig)
    show_scrollable(path, height=DISPLAY_HEIGHT*len(plots))
    return path

def get_turn_label(row, max_length=120, line_length=30):
    """The text of a turn for the x-axis: the turn number, the speaker and the utterance wrapped over short lines."""
    text = row['utterance']
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    lines = ['']
    for word in text.split():
        if lines[-1] and len(lines[-1]) + len(word) > line_length:
            lines.append('')
        lines[-1] += word + ' '
    return f"{row['turn']} {row['speaker'].upper()}:\n" + '\n'.join(line.strip() for line in lines)

def set_turn_labels(ax, turn_labels):
    """Puts a tick for every turn on the x-axis with the turn number, the speaker and the utterance as label."""
    turns = sorted(turn_labels)
    ax.set_xticks(turns)
    ax.set_xticklabels([turn_labels[turn] for turn in turns], rotation=90, size='small', linespacing=1.3)
    ax.set_xlim(turns[0] - 0.5, turns[-1] + 0.5)
    ax.set_xlabel('')

def scale_scores(rows):
    """Divides the scores by the largest absolute score, so that all scores fall between -1 and 1 and 0 stays 0."""
    largest = max(abs(row['score']) for row in rows) or 1
    return [{**row, 'score': row['score'] / largest} for row in rows]

def create_combined_timeline_image_from_csvs(emissor_path, scenario, settings: PlotSettings, metrics=None, scores=None,
                                             scale=True, turn_column='Turn', speaker_column='Speaker',
                                             text_column='Response'):
    """Plots the scores of all csv files in the evaluation folder of a scenario as lines in a single plot,
    with a different colour for each evaluation score and a different line style for each speaker.
    The text of the turns is shown on the x-axis, since all csv files share the same turns.
    metrics: optional list of substrings, only csv files with one of them in the filename are plotted
    scores: optional dictionary from a substring of the filename to the score column to plot, e.g. {'manual': 'Coherent'},
            added to DEFAULT_SCORES; for other files the first numeric column is plotted
    scale: divide each score by its largest absolute value, so that scores with different ranges (e.g. llh from 0 to 1
           and da_score from -5 to 5) can be compared in the same plot
    The image is saved in the evaluation folder as <scenario>_combined_plot.png and its path is returned."""
    evaluation_folder = os.path.join(emissor_path, scenario, "evaluation")
    plots = get_csv_plots(emissor_path, scenario, settings, metrics, scores, turn_column, speaker_column, text_column)
    if not plots:
        print('No csv files to plot in', evaluation_folder)
        return

    data = []
    turn_labels = {}
    for name, score_column, rows in plots:
        for row in (scale_scores(rows) if scale else rows):
            data.append({'turn': row['turn'], 'score': row['score'], 'speaker': row['speaker'],
                         'evaluation': f"{name}: {score_column}", 'annotation': row['annotation']})
            turn_labels.setdefault(row['turn'], get_turn_label(row))
    df = pd.DataFrame(data)

    set_plot_style()
    fig, ax = plt.subplots(figsize=(max(10, TURN_WIDTH*len(turn_labels)), PLOT_HEIGHT))
    evaluations = list(df['evaluation'].unique())
    palette = dict(zip(evaluations, sns.color_palette("deep", len(evaluations))))
    sns.lineplot(x='turn', y='score', data=df, hue='evaluation', style='speaker', markers=True, dashes=True,
                 palette=palette, linewidth=2.5, markersize=12, ax=ax)
    # the speaker and the unscaled score next to each point, in the colour of its line
    for _, row in df.iterrows():
        ax.annotate(get_point_label(row), (row['turn'], row['score']), xytext=(8, 4), textcoords='offset points',
                    size='x-small', color=palette[row['evaluation']], verticalalignment='bottom',
                    linespacing=1.2, bbox=LABEL_BOX, rotation=POINT_LABEL_ROTATION, rotation_mode='anchor')
    set_turn_labels(ax, turn_labels)
    ax.set_ylabel('scaled score' if scale else 'score')
    if scale:
        ax.set_ylim(-1.1, 1.1)
    ax.axhline(0, color='grey', linestyle=':', linewidth=1)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), frameon=True)
    ax.set_title(scenario, loc='left', fontweight='bold')

    name = scenario + "_combined"
    if settings._START>0:
        name += "_S"+ str(settings._START)
    if settings._END>-1:
        name += "_E"+str(settings._END)
    path = os.path.join(evaluation_folder, name + "_plot.png")
    fig.savefig(path, bbox_inches='tight')
    print('Saved plot to', path)
    plt.close(fig)
    show_scrollable(path)
    return path



def process_all_scenarios(emissor:str, scenarios:[], settings):
        if len(scenarios)==0:
            scenario = os.listdir(emissor)
        for scenario in scenarios:
            if not scenario.startswith("."):
                scenario_path = os.path.join(emissor, scenario)
                has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
                check_message = "Scenario:" + scenario + "\n"
                check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
                check_message += "\tText JSON:" + str(has_text) + "\n"
                check_message += "\tImage JSON:" + str(has_image) + "\n"
                check_message += "\tRDF :" + str(has_rdf) + "\n"
                print(check_message)
                if not has_scenario:
                    print("No scenario JSON found. Skipping:", scenario_path)
                elif not has_text:
                    print("No text JSON found. Skipping:", scenario_path)
                else:
                    create_timeline_image(emissor_path=emissor, scenario=scenario, settings=settings)

def main(emissor_path:str, scenario:str, annotations:[], sentiment_threshold=0, llh_threshold=0, start=0, end=-1, csv_file='', score_column='', label_column=None, stacked=False, combined=False):
    settings = PlotSettings()
    if annotations:
        settings._ANNOTATIONS = annotations
    if sentiment_threshold > 0:
        settings._SENTIMENT_THRESHOLD = sentiment_threshold
    if llh_threshold > 0:
        settings._LLH_THRESHOLD = llh_threshold
    if start > 0:
        settings._START = start
    if end > -1:
        settings._END = end

    if csv_file:
        create_timeline_image_from_csv(csv_file, score_column, settings, emissor_path, scenario, label_column=label_column)
        return
    if stacked:
        create_stacked_timeline_image_from_csvs(emissor_path, scenario, settings)
        return
    if combined:
        create_combined_timeline_image_from_csvs(emissor_path, scenario, settings)
        return

    print("_ANNOTATIONS", settings._ANNOTATIONS)
    print("_SENTIMENT_THRESHOLD", settings._SENTIMENT_THRESHOLD)
    print("_LLH_THRESHOLD", settings._LLH_THRESHOLD)
    folders = []
    if not scenario:
        folders = os.listdir(emissor_path)
    else:
        folders=[scenario]
    process_all_scenarios(emissor_path, folders, settings)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor-path', type=str, required=False, help="Path to the emissor folder", default='')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    parser.add_argument('--sentiment_threshold', type=float, required=False, help="Threshold for dialogue_act, sentiment and emotion scores", default=0.5)
    parser.add_argument('--llh_threshold', type=float, required=False, help="Threshold below which likelihood becomes negative", default=0.3)
    parser.add_argument('--annotations', type=str, required=False, help="Annotations to be considered for scoring: 'go, sentiment, ekman, llh'" , default='llh')
    parser.add_argument('--start', type=int, required=False, help="Starting signal for plotting" , default=0)
    parser.add_argument('--end', type=int, required=False, help="End signal for plotting, -1 means until the last signal" , default=-1)
    parser.add_argument('--csv', type=str, required=False, help="Csv file with the columns Turn, Speaker, Response and a score column to plot instead of the EMISSOR annotations", default='')
    parser.add_argument('--score', type=str, required=False, help="Name of the score column in the csv file, e.g. llh or llm_coherence", default='')
    parser.add_argument('--label', type=str, required=False, help="Column in the csv file with a value to add to the label of each data point, e.g. dialogue_act or go_emotion", default=None)
    parser.add_argument('--stacked', action='store_true', help="Plot all csv files in the evaluation folder of the scenario under each other in one image")
    parser.add_argument('--combined', action='store_true', help="Plot the scores of all csv files in the evaluation folder of the scenario as lines in one plot")
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)

    main(emissor_path=args.emissor_path,
         scenario=args.scenario,
         annotations=args.annotations,
         llh_threshold=args.llh_threshold,
         sentiment_threshold=args.sentiment_threshold,
         start=args.start,
         end=args.end,
         csv_file=args.csv,
         score_column=args.score,
         label_column=args.label,
         stacked=args.stacked,
         combined=args.combined)
