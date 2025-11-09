"""Utility functions for Japanese text processing."""

import csv
import re
from typing import Iterable, NamedTuple, Sequence

import MeCab


def either(strings: Iterable[str]) -> re.Pattern[str]:
    """Create a regular expression pattern that matches any of the given strings.

    Parameters
    ----------
    strings : Iterable[str]
        Input strings.

    Returns
    -------
    re.Pattern[str]
        Regular expression pattern.
    """
    strings = sorted(strings, key=len, reverse=True)

    result2 = []

    prefix = {}
    for s in strings:
        if len(s) < 2:
            continue
        c1 = s[0]
        if c1 not in prefix:
            prefix[c1] = {s[1:]}
        else:
            prefix[c1].add(s[1:])

    frozen_prefix = {
        k: frozenset(prefix[k])
        for k in sorted(prefix, key=lambda x: (-len(prefix[x]), x, prefix[x]))
    }

    seen = set()
    for c1, s1 in frozen_prefix.items():
        if s1 in seen:
            continue
        seen.add(s1)
        a = [c1]
        for c2, s2 in frozen_prefix.items():
            if c1 != c2 and s1 == s2:
                a.append(c2)
        if len(a) >= 2:
            p1 = "[" + "".join(re.escape(c) for c in sorted(a)) + "]"
        else:
            p1 = re.escape(c1)
        if len(s1) >= 2:
            if any(len(s) > 1 for s in s1):
                p2 = (
                    "(?:"
                    + "|".join(
                        re.escape(c) for c in sorted(s1, key=lambda x: (-len(x), x))
                    )
                    + ")"
                )
            else:
                p2 = "[" + "".join(re.escape(c) for c in sorted(s1)) + "]"
        else:
            p2 = re.escape(next(iter(s1)))
        result2.append(p1 + p2)

    result2.sort(key=lambda x: (-len(x), x))

    result1 = []

    for s in strings:
        if len(s) == 1:
            result1.append(re.escape(s))

    result1.sort(key=lambda x: (-len(x), x))
    if len(result1) >= 2:
        result1 = ["[" + "".join(result1) + "]"]

    result = result2 + result1

    return re.compile("|".join(result))


def _init_to_vowel() -> tuple[dict[int, str], re.Pattern[str], dict[str, str]]:
    to_vowel_map1 = {}
    for a, s in (
        ("ア", "カサタナハマヤラワア゙ガザダバヷパァ"),
        ("イ", "キシチニヒミリヰギジヂビヸピィ"),
        ("ウ", "クスツヌフムユルグズヅブヴプゥ"),
        ("エ", "ケセテネヘメレヱゲゼデベヹペェ"),
        ("オ", "コソトノホモヨロヲゴゾドボヺポォ"),
    ):
        for c in s:
            to_vowel_map1[c] = a

    to_vowel_table = str.maketrans(to_vowel_map1)

    to_vowel_map2 = {}

    for a, s, b in (
        # open yo-on
        ("ア", "キシチニヒミリギジヂビヸピ", "ャ"),
        ("ウ", "キシチニヒミリギジヂビヸピ", "ュ"),
        ("オ", "キシチニヒミリギジヂビヸピ", "ョ"),
        # closed yo-on
        ("ア", "クグ", "ヮ"),
        # cyoku-on
        ("ア", "ツフヴ", "ァ"),
        ("イ", "ステツフズデヴ", "ィ"),
        ("ウ", "トホド", "ゥ"),
        ("エ", "シチツフジヴ", "ェ"),
        ("オ", "ツフヴ", "ォ"),
        # open yo-on
        ("エ", "イキニヒピミリギビ", "ェ"),
        ("ア", "ステツフズデヴ", "ャ"),
        ("ウ", "ステツフズデヴ", "ュ"),
        ("オ", "ステツフズデヴ", "ョ"),
        # closed yo-on
        ("ア", "クスヌプムルグズブ", "ァ"),
        ("イ", "ウクヌプムルグブ", "ィ"),
        ("エ", "ウクスヌプムルグズブ", "ェ"),
        ("オ", "ウクスヌプムルグズブ", "ォ"),
    ):
        for c in s:
            to_vowel_map2[c + b] = a

    to_vowel_re = either(to_vowel_map2)

    return to_vowel_table, to_vowel_re, to_vowel_map2


_to_vowel_table, _to_vowel_re, _to_vowel_map = _init_to_vowel()


def katakana_to_vowels(text: str) -> str:
    """Convert a katakana string to the corresponding sequence of vowels.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Converted text.

    Example
    -------
    >>> katakana_to_vowels("コンピューター")
    'オンウーアー'
    """
    s = re.sub(_to_vowel_re, lambda m: _to_vowel_map[m.group(0)], text)
    return s.translate(_to_vowel_table)


def count_mora_in_katakana(text: str) -> int:
    """Count the number of mora in a katakana string.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    int
        Number of mora.

    Example
    -------
    >>> count_mora_in_katakana("コンピューター")
    6
    """
    return _count_mora_in_katakana(katakana_to_vowels(text))


def _count_mora_in_katakana(text: str) -> int:
    return len(re.findall(r"[アイウエオッンー]", text))


class Word(NamedTuple):
    """Parsed Word."""

    surface: str
    pos1: str
    pos2: str
    pos3: str
    pos4: str
    cType: str  # noqa: N815
    cForm: str  # noqa: N815
    lForm: str  # noqa: N815
    lemma: str
    orth: str
    pron: str
    orthBase: str  # noqa: N815
    pronBase: str  # noqa: N815
    goshu: str
    iType: str  # noqa: N815
    iForm: str  # noqa: N815
    fType: str  # noqa: N815
    fForm: str  # noqa: N815
    kana: str
    kanaBase: str  # noqa: N815
    form: str
    formBase: str  # noqa: N815
    iConType: str  # noqa: N815
    fConType: str  # noqa: N815
    aType: str  # noqa: N815
    aConType: str  # noqa: N815
    aModType: str  # noqa: N815
    vowels: str
    mora: int
    wcost: int


def parse(text: str) -> Sequence[Word]:
    """Parse a text into words."""
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    result: list[Word] = []
    while node:
        surface = node.surface
        if surface:
            features = next(csv.reader([node.feature]))

            if len(features) < 26:
                features += ["*"] * (26 - len(features))

            pron = features[9]
            vowels = katakana_to_vowels(pron)
            mora = _count_mora_in_katakana(vowels)
            wcost = node.wcost
            word = Word(
                surface, *features, vowels, mora, wcost  # type: ignore[arg-type]
            )  # type: ignore[call-arg]
            result.append(word)
        node = node.next
    return tuple(result)
