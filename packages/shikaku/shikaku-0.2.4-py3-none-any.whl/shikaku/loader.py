"""Text loaders."""

import functools
import io
import re
import urllib.request
import warnings
import zipfile


@functools.cache
def _download(url: str) -> bytes:
    """
    Return the file contents downloaded from the given URL.

    Parameters
    ----------
    url : str
        URL for downloading data.

    Returns
    -------
    bytes
        Downloaded data.

    """
    with urllib.request.urlopen(url) as f:  # noqa: S310
        return f.read()  # type: ignore[no-any-return]


def _remove_annotations(text: str) -> str:
    """
    Remove annotations in the text.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Processed text.

    """
    text = re.split(r"\-{5,}", text)[2]  # remove header
    text = re.split("底本：", text)[0]  # remove footer
    text = re.sub("｜", "", text)  # beginning of string with ruby
    text = re.sub("《.+?》", "", text)  # ruby
    text = re.sub("［＃.+?］", "", text)  # comments by staff
    text = text.strip()
    return text


class AozoraBunkoFileError(ValueError):
    """Error raised for unexpected format in files on Aozora Bunko."""


class AozoraBunkoFileWarning(Warning):
    """Warning raised for unexpected format in files on Aozora Bunko."""


def load_aozorabunko(author_id: int, work_id: int, *, raw: bool = False) -> str:
    """
    Return text downloaded from Aozora Bunko (GitHub mirror).

    Parameters
    ----------
    author_id : int
        Author ID.
    work_id : int
        Work ID.
    raw : bool, default False
        Whether it returns a raw text or not.

    Returns
    -------
    str
        Downloaded text.

    Example
    -------
    >>> load_aozorabunko(35, 1567)  # doctest: +SKIP
    ... # author_id: 35, work_id: 1567 => "Run, Melos!"

    """
    # Download the corresponding library card.
    card_file = f"{author_id:0=6}/card{work_id}.html"
    card = _download(
        "https://raw.githubusercontent.com/aozorabunko/aozorabunko/master/cards/"
        f"{card_file}"
    ).decode("utf-8")

    # Search for the ZIP file with ruby text from the library card.
    m = re.search(r"\d+_ruby_\d+\.zip", card)
    if not m:
        # Fallback to the ZIP file without ruby text.
        m = re.search(r"\d+_txt_\d+\.zip", card)
        if not m:
            raise AozoraBunkoFileError(f"ZIP file not detected in {card_file}")
    zipname = m.group(0)

    # Download the ZIP file.
    zipdata = zipfile.ZipFile(
        io.BytesIO(
            _download(
                "https://raw.githubusercontent.com/"
                "aozorabunko/aozorabunko/master/cards/"
                f"{author_id:0=6}/files/{zipname}"
            )
        )
    )

    # Find text files in the ZIP file.
    text_filenames = [s for s in zipdata.namelist() if s.lower().endswith(".txt")]
    if not text_filenames:
        raise AozoraBunkoFileError(f"text file not found in {zipname}")
    if len(text_filenames) >= 2:
        warnings.warn(
            f"more than one text files found: {text_filenames}. Take the first one",
            AozoraBunkoFileWarning,
            stacklevel=2,
        )
    filename = text_filenames[0]

    # Extract text from the ZIP file.
    text = zipdata.read(filename).decode("shift-jis")

    if not raw:
        text = _remove_annotations(text)

    return text
