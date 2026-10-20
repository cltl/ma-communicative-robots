"""A chat window for a notebook, in which the questions of an agent and the answers of the user are shown together.

The agent needs a start() method that returns the first utterance, a respond(utterance) method that returns the next
utterance and a done property that is True when the conversation is finished, such as the DayInterviewer.
"""
import html

import ipywidgets as widgets
from IPython.display import display

STOP_UTTERANCE = "stop"

BUBBLE_STYLE = ("display:inline-block; max-width:75%; padding:0.4em 0.7em; margin:0.2em 0; border-radius:0.7em; "
                "white-space:pre-wrap; text-align:left; color:black; background:{color};")
AGENT_COLOR = "#e9e9eb"
USER_COLOR = "#cfe3ff"


class ChatWindow():
    def __init__(self, agent, height="450px", font_size=18):
        """Creates a chat window for the agent.
        params
        agent: the agent to talk to
        height: height of the part of the window with the conversation, it scrolls when the conversation gets longer
        font_size: font size in pixels at the start, it can be changed with the slider in the window
        """
        self.agent = agent
        self.busy = False
        self.messages = []
        self.conversation = widgets.HTML(layout=widgets.Layout(flex="none"))
        # a reversed column keeps the box scrolled down to the newest message
        self.conversation_box = widgets.Box([self.conversation], layout=widgets.Layout(
            height=height, overflow_y="auto", border="1px solid #ccc", padding="8px", flex_flow="column-reverse"))
        # the answer is sent with enter, observing the value with continuous_update=False
        self.answer = widgets.Text(placeholder="Type your answer and press enter", continuous_update=False,
                                   layout=widgets.Layout(flex="1"))
        self.answer.observe(self.on_answer, "value")
        self.skip_button = widgets.Button(description="Skip question", tooltip="Answer nothing, e.g. to skip an hour")
        self.skip_button.on_click(lambda button: self.send(""))
        self.stop_button = widgets.Button(description="Stop", button_style="danger",
                                          tooltip="End the conversation and save the day")
        self.stop_button.on_click(lambda button: self.send(STOP_UTTERANCE))
        self.font_size = widgets.IntSlider(value=font_size, min=10, max=36, description="Font size",
                                           continuous_update=False)
        self.font_size.observe(lambda change: self.set_font_size(), "value")
        self.status = widgets.HTML()
        self.saved = widgets.HTML()
        self.window = widgets.VBox([self.font_size,
                                    self.conversation_box,
                                    widgets.HBox([self.answer, self.skip_button, self.stop_button]),
                                    self.status,
                                    self.saved])
        self.set_font_size()

    def show(self):
        display(self.window)
        self.add_message("Agent", self.agent.start())

    def set_font_size(self):
        size = f"{self.font_size.value}px"
        for widget in [self.answer, self.skip_button, self.stop_button, self.status, self.saved]:
            widget.style.font_size = size
        # the text field and the buttons grow with the font
        height = f"{round(self.font_size.value * 2.2)}px"
        for widget in [self.answer, self.skip_button, self.stop_button]:
            widget.layout.height = height
        self.skip_button.layout.width = f"{self.font_size.value * 8}px"
        self.stop_button.layout.width = f"{self.font_size.value * 5}px"
        self.render()

    def add_message(self, speaker, text):
        self.messages.append((speaker, text))
        self.render()

    def render(self):
        """Shows the conversation: the agent on the left and the user on the right."""
        bubbles = []
        for speaker, text in self.messages:
            align = "right" if speaker == "You" else "left"
            color = USER_COLOR if speaker == "You" else AGENT_COLOR
            text = html.escape(text) if text else "<i>(no answer)</i>"
            bubbles.append(f'<div style="text-align:{align};"><div style="{BUBBLE_STYLE.format(color=color)}">'
                           f'<b>{speaker}:</b> {text}</div></div>')
        self.conversation.value = (f'<div style="font-size:{self.font_size.value}px; line-height:1.4;">'
                                   + "".join(bubbles) + '</div>')

    def on_answer(self, change):
        # clearing the text field after sending also changes the value, which is not an answer
        if change["new"] and not self.busy:
            self.send(change["new"])

    def send(self, utterance):
        if self.busy or self.agent.done:
            return
        self.busy = True
        self.set_enabled(False)
        self.answer.value = ""
        self.add_message("You", utterance)
        self.status.value = "<i>The agent is thinking...</i>"
        try:
            self.add_message("Agent", self.agent.respond(utterance))
        except Exception as e:
            self.add_message("Agent", f"Sorry, something went wrong: {e}")
        finally:
            self.busy = False
            self.status.value = ""
            self.set_enabled(not self.agent.done)
        if getattr(self.agent, "path", None):
            nr_of_events = len(getattr(self.agent, "day", {}))
            self.saved.value = f"<i>Saved {nr_of_events} event(s) to {html.escape(self.agent.get_display_path())}</i>"
        if self.agent.done:
            self.status.value = "<i>The conversation is finished.</i>"

    def set_enabled(self, enabled):
        for widget in [self.answer, self.skip_button, self.stop_button]:
            widget.disabled = not enabled
