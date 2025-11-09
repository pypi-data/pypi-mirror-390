"""Word cloud."""

from dataclasses import dataclass
from typing import Any, Optional

import matplotlib_fontja
import MeCab
import PIL.Image
import wordcloud


@dataclass(frozen=True)
class WordCloudResult:
    """Word cloud result."""

    wordcloud: wordcloud.WordCloud

    def _repr_png_(self) -> Any:
        return self.wordcloud.to_image()._repr_png_()

    def to_file(self, filename: str) -> None:
        """
        Write the word cloud image into the given file.

        Parameters
        ----------
        filename : str
            Filename to be written.

        """
        self.wordcloud.to_file(filename)

    def to_image(self) -> PIL.Image.Image:
        """
        Return the PIL image of the word cloud.

        Returns
        -------
        PIL.Image.Image
            Image of the word cloud.
        """
        return self.wordcloud.to_image()  # type: ignore[no-any-return]


def _get_words(text: str) -> str:
    """Extract words suitable for word cloud."""
    words = []
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    while node:
        a = node.feature.split(",")
        if a[0] == "名詞" and (a[1] == "普通名詞" or a[1] == "固有名詞"):
            words.append(node.surface)
        node = node.next
    return " ".join(words)


class WordCloud:
    """Word cloud."""

    def __init__(
        self,
        *,
        width: int = 480,
        height: int = 320,
        background_color: str = "white",
    ):
        """
        Construct a word cloud.

        Parameters
        ----------
        width : int, default 480
            Width of the canvas.
        height : int, default 320
            Height of the canvas.
        background_color : str, default "white"
            Background color for the word cloud image.
        """
        self._width = width
        self._height = height
        self._background_color = background_color
        self._words: Optional[str] = None

    def _create(self, seed: Optional[int]) -> wordcloud.WordCloud:
        return wordcloud.WordCloud(
            font_path=matplotlib_fontja.get_font_ttf_path(),
            width=self._width,
            height=self._height,
            background_color=self._background_color,
            random_state=seed,
        )

    def fit(self, text: str) -> None:
        """
        Train the model.

        Parameters
        ----------
        text : str
            Text for training.

        """
        text = _get_words(text)
        wc = self._create(1)
        self._words = wc.process_text(text)

    def generate(
        self,
        seed: Optional[int] = None,
    ) -> WordCloudResult:
        """
        Generate a word cloud.

        Parameters
        ----------
        seed : int, optional
            Random seed.

        Returns
        -------
        WordCloudResult
            Generated word cloud.

        """
        if self._words is None:
            raise ValueError("model is not yet trained")

        wc = self._create(seed)
        result = wc.generate_from_frequencies(self._words)
        return WordCloudResult(result)
