"""Markov chain model."""

import random
import re
import types
from typing import Any, Optional

import igraph as ig
import markovify
import matplotlib.axes
import matplotlib.pyplot as plt
import MeCab
from markovify.chain import BEGIN, END


def _preprocess_text(text: str) -> list[str]:
    """
    Preprocess the text.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    list[str]
        Sentences.

    """
    tagger = MeCab.Tagger("-Owakati")

    result = []

    for line in text.splitlines():
        line = line.strip()
        line = line.lstrip("　")
        if not line:
            continue

        # Handle brackets.
        if any(c in line for c in "「」（）"):
            while True:
                # "「...」" -> "..."
                if (
                    line[:1] == "「"
                    and line[-1:] == "」"
                    and "「" not in line[1:-1]
                    and "」" not in line[1:-1]
                ):
                    line = line[1:-1].strip()
                    continue
                # "...「...」" -> "......"
                line1 = re.sub("「([^「」]+)」$", r"\g<1>", line)
                if line1 != line:
                    line = line1.strip()
                    continue
                # "（...）" -> "..."
                if (
                    line[:1] == "（"
                    and line[-1:] == "）"
                    and "（" not in line[1:-1]
                    and "）" not in line[1:-1]
                ):
                    line = line[1:-1].strip()
                    continue
                break
            # Remove possibly incomplete sentences,
            # "...「...」...。..." -> "..."
            while True:
                line1 = re.sub(
                    "^[^「」]*「[^「」]*」[^「」。！？!?]*[。！？!?]+", "", line
                )
                if line1 != line:
                    line = line1.strip()
                    continue
                break
            # Check if brackets are still there.
            # It possibly contains incomplete sentences.
            # TODO: case of "「noun」".
            if any(c in line for c in "「」（）"):
                continue

        if not line:
            continue

        # Remove incomplete sentences.
        line = re.sub("[^。！？!?]+$", "", line)

        if not line:
            continue

        line = re.sub("[。！？!?]+", r"\g<0>.", line)
        line = re.sub(r"。+\.", ".", line)
        line = tagger.parse(line).rstrip()
        line = re.sub(r"\s+\.", ".", line)
        result += line.split(".")

    result = [x.strip() for x in result if x]
    result = [x for x in result if x]
    return result


def _custom_word_split(self: "TextModel", sentence: str) -> list[str]:
    tagger = MeCab.Tagger("-Owakati")
    words = tagger.parse(sentence.rstrip("。")).rstrip().split(" ")
    return words  # type: ignore[no-any-return]


def _custom_word_join(self: "TextModel", words: list[str]) -> str:
    sentence = "".join(words)
    if sentence and sentence[-1] not in "。！？!?":
        sentence = sentence + "。"
    return sentence


def _do_monkey_patch(model: markovify.Text) -> None:
    model.word_split = types.MethodType(_custom_word_split, model)
    model.word_join = types.MethodType(_custom_word_join, model)


class TextModel:
    """Text generation model by Markov chain."""

    def __init__(self, state_size: int = 2) -> None:
        """
        Construct a text generation model.

        Parameters
        ----------
        state_size : int, default 2
            Markov chain state size.

        """
        self._state_size = state_size
        self._model: Optional[markovify.Text] = None
        self._compiled_model: Optional[markovify.Text] = None

    def fit(self, text: str) -> None:
        """
        Train the model.

        Parameters
        ----------
        text : str
            Text for training.

        """
        # Build a model.
        model = markovify.Text(
            _preprocess_text(text), state_size=self._state_size, well_formed=False
        )

        self._model = model
        self._compiled_model = None

    def generate(
        self,
        *,
        beginning: Optional[str] = None,
        strict: Optional[bool] = None,
        tries: Optional[int] = None,
        min_words: Optional[int] = None,
        max_words: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Optional[str]:
        """
        Generate a sentence.

        Parameters
        ----------
        beginning : str, optional
            Beginning word.
        strict : bool, optional
            Whether to strictly use the beginning word or not.
        tries : int, optional
            Number of tries to generate a valid sentence.
        min_words : int, optional
            Minimum number of words.
        max_words : int, optional
            Maximum number of words.
        seed : int, optional
            Random seed.

        Returns
        -------
        str or None
            Generated sentence.

        """
        if self._model is None:
            raise ValueError("model is not yet trained")

        if seed is not None:
            random.seed(seed)

        if self._compiled_model is None:
            self._compiled_model = self._model.compile()
            _do_monkey_patch(self._compiled_model)

        args: dict[str, Any] = {}
        if beginning is not None:
            args["beginning"] = beginning
        if strict is not None:
            args["strict"] = strict
        if tries is not None:
            args["tries"] = tries
        if min_words is not None:
            args["min_words"] = min_words
        if max_words is not None:
            args["max_words"] = max_words

        m = self._compiled_model
        if beginning is None:
            s = m.make_sentence(**args)
        else:
            s = m.make_sentence_with_start(**args)
        return s  # type: ignore[no-any-return]

    def plot(
        self,
        *,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dpi: Optional[int] = None,
        layout: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> matplotlib.axes.Axes:
        """
        Plot the model.

        Parameters
        ----------
        width: float, optional
            Width of the figure.
        height: float, optional
            Height of the figure.
        dpi: int, optional
            Resolution of the figure.
        layout: str, optional
            Layout of the graph.
        seed : int, optional
            Random seed.

        Returns
        -------
        matplotlib.axes.Axes :
            Matplotlib axes containing the plot.

        """
        if self._model is None:
            raise ValueError("model is not yet trained")

        if width is None:
            width = 10
        if height is None:
            height = width

        if seed is not None:
            random.seed(seed)

        m = self._model.chain.model
        n = self._model.state_size
        beginning_state = (BEGIN,) * n
        ending_state = (END,)

        vertices: dict[tuple[str, ...], int] = {}
        edges = []
        weights = []

        def get_state_name(state: tuple[str, ...]) -> str:
            if all(x == BEGIN for x in state):
                return "BEGIN"
            if END in state:
                return "END"
            s = list(state)
            while s[0] == BEGIN:
                del s[0]
            return ",".join(s)

        def traverse(state: tuple[str, ...]) -> None:
            if state in vertices:
                return
            vertices[state] = len(vertices)

            if state not in m:
                return

            total_weight = sum(m[state].values())

            for next_word, weight in m[state].items():
                if next_word == END:
                    next_state = ending_state
                else:
                    next_state = state[1:] + (next_word,)
                traverse(next_state)
                edges.append((vertices[state], vertices[next_state]))
                weights.append(weight / total_weight)

        traverse(beginning_state)

        _, ax = plt.subplots(figsize=(width, height), dpi=dpi)

        g = ig.Graph(len(vertices), edges, directed=True)
        ig.plot(
            g,
            target=ax,
            layout=layout,
            vertex_label=[get_state_name(x) for x in vertices],
            vertex_color="#f99",
            vertex_frame_color="#999",
            edge_label=[f"{x:.02f}" for x in weights],
            edge_color="#999",
            edge_label_color="#33f",
            edge_width=0.5,
            edge_arrow_width=10,
            edge_arrow_size=10,
            edge_align_label=True,
        )

        return ax
