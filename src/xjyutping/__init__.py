"""Cantonese Jyutping (粵拼) for traditional Chinese text, with each reading
chosen from the words around it.

The Python port of the xjyutping LaTeX package: the same data and the same
segmentation, so both give the same readings.  The API follows xpinyin::

    >>> from xjyutping import Jyutping
    >>> j = Jyutping()
    >>> j.get_jyutping('我哋去銀行')
    'ngo5-dei6-heoi3-ngan4-hong4'
"""
import re
from itertools import groupby, islice, product
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

__version__ = '1.3.0'
__all__ = ['Jyutping', 'Segment', 'TONE_MARKS']

DATA_DIR = Path(__file__).resolve().with_name('data')

# Tone symbols of Visual Jyutping (https://github.com/VincentTam/visual-jyutping,
# MIT licence): webToneMap and dcToneMap in assets/js/script.js.
TONE_MARKS = {
    'fancy': {'1': 'ˉ¹', '2': 'ˊ²', '3': '˗₃',
              '4': 'ˎ₄', '5': 'ˏ₅', '6': 'ˍ₆'},
    'discord': {'1': 'ˉ¹', '2': '⸍²', '3': '-₃',
                '4': '⸜₄', '5': '⸝₅', '6': 'ˍ₆'},
}
CONVERTS = ('lower', 'upper', 'capitalize')
_INITIAL = re.compile(r'(?:ng|gw|kw|[bpmfdtnlgkhwzcsj])(?=[a-z])')


class Segment(NamedTuple):
    """A word or a single character of a run of Chinese text."""
    text: str             # its characters (spaces inside a run left out)
    readings: List[str]   # one Jyutping syllable per character
    type: str             # w word, u user setting, m guessed polyphone,
    #                       s character with a single common reading


def _table(path: Path) -> List[List[str]]:
    with open(path, encoding='utf8') as f:
        return [line.rstrip('\n').split('\t') for line in f]


class Jyutping:
    """Translate traditional Chinese characters to Cantonese Jyutping.

    >>> j = Jyutping()
    >>> j.get_jyutping('銀行')
    'ngan4-hong4'
    >>> j.get_jyutping('行路', ' ', tone_marks='fancy')
    'haangˎ₄ louˍ₆'
    """

    def __init__(self, data_dir: Optional[str] = None) -> None:
        d = Path(data_dir) if data_dir else DATA_DIR
        # char -> (default reading, other readings, polyphone?); a fifth
        # column, if any, is the cost of the character standing alone
        self._chars: Dict[str, Tuple[str, List[str], bool]] = {}
        self._cost: Dict[str, int] = {}                    # char or word -> cost
        for row in _table(d / 'chars.tsv'):
            self._chars[row[0]] = (row[1], row[2].split(), row[3] == '1')
            if len(row) > 4:
                self._cost[row[0]] = int(row[4])
        self._finals = dict(_table(d / 'finals.tsv'))      # reading at run end
        self._variants = dict(_table(d / 'variants.tsv'))  # variant -> canonical
        self._words: Dict[str, str] = {}                   # word -> 'r1 r2 ...'
        for row in _table(d / 'words.tsv'):
            self._words[row[0]] = row[1]
            if len(row) > 2:
                self._cost[row[0]] = int(row[2])
        # a character and the one or two after it -> the character's reading
        # when it stands alone before them (呢 before a classifier: ni1)
        nxt = d / 'next.tsv'
        self._next = dict(_table(nxt)) if nxt.exists() else {}
        self._longest: Dict[str, int] = {}                 # final char -> length
        for w in self._words:
            if len(w) > self._longest.get(w[-1], 0):
                self._longest[w[-1]] = len(w)
        self._user_chars: Dict[str, str] = {}
        self._user_words: Set[str] = set()

    # --- formatting ----------------------------------------------------

    @staticmethod
    def decode_jyutping(syllable: str, tone_marks: Optional[str] = 'numbers') -> str:
        """Write the tone of a syllable such as 'hong4' in the given style:
        'numbers' (hong4), None (hong), 'fancy' (hongˎ₄) or 'discord' (hong⸜₄)."""
        if tone_marks == 'numbers':
            return syllable
        if tone_marks is None:
            return syllable.rstrip('123456')
        if tone_marks not in TONE_MARKS:
            raise ValueError('unknown tone_marks %r' % (tone_marks,))
        tone = syllable[-1:]
        marks = TONE_MARKS[tone_marks]
        return syllable[:-1] + marks[tone] if tone in marks else syllable

    @staticmethod
    def convert_jyutping(word: str, convert: str = 'lower') -> str:
        """Apply 'lower', 'upper' or 'capitalize' to a syllable."""
        if convert not in CONVERTS:
            raise ValueError('unknown convert %r' % (convert,))
        return getattr(word, convert)()

    # --- readings --------------------------------------------------------

    def set_jyutping(self, text: str, reading: str) -> None:
        """Give one character a new default reading, or a word (several
        characters, one syllable each) a reading that beats the word list.
        Whitespace in text is ignored, as \\setjyutping ignores it."""
        text = re.sub('[ \t\r\n]', '', text)
        syllables = reading.split()
        if not text or len(syllables) != len(text):
            raise ValueError('%r has %d character(s) but %r has %d syllable(s)'
                             % (text, len(text), reading, len(syllables)))
        if len(text) == 1:
            self._user_chars[text] = syllables[0]
            return
        for w in (text, self._canon(text)):
            self._words[w] = ' '.join(syllables)
            self._cost[w] = 0            # a user's word wins ties
            self._user_words.add(w)
            self._longest[w[-1]] = max(self._longest.get(w[-1], 0), len(w))

    def segment(self, text: str) -> List[Segment]:
        """The words and single characters the Chinese text is read as, with
        their readings and types (what the TeX package's debug option logs)."""
        return [s for run in self._runs(text)
                for s in self._segment_run(''.join(text[i] for i in run))]

    def annotate(self, text: str, tone_marks: Optional[str] = 'numbers'
                 ) -> List[Tuple[str, Optional[str]]]:
        """(character, reading) for every character of text; the reading is
        None for anything that is not a Chinese character."""
        self.decode_jyutping('', tone_marks)    # reject an unknown style early
        return [(c, None if r is None else self.decode_jyutping(r, tone_marks))
                for c, r in zip(text, self._readings(text))]

    def get_jyutpings(self, chars: str, splitter: str = '-',
                      tone_marks: Optional[str] = 'numbers', convert: str = 'lower',
                      n: int = 10) -> List[str]:
        """Up to n combinations of readings: the reading in context first for
        each character, then its other readings."""
        def fmt(s: str) -> str:
            return self.convert_jyutping(self.decode_jyutping(s, tone_marks), convert)
        fmt('')                                  # reject unknown styles early
        readings = self._readings(chars)
        options: List[List[str]] = []
        for han, group in groupby(range(len(chars)), lambda i: readings[i] is not None):
            idx = list(group)
            if not han:     # kept as it is, but not spaces between characters
                stretch = chars[idx[0]:idx[-1] + 1]
                if not (stretch.isspace() and 0 < idx[0] and idx[-1] + 1 < len(chars)):
                    options.append([stretch])
                continue
            for i in idx:
                default, others, _ = self._chars.get(chars[i], (readings[i], [], False))
                forms = [fmt(r) for r in [readings[i], default] + others]
                options.append(list(dict.fromkeys(forms)))
        return [splitter.join(c) for c in islice(product(*options), n)]

    def get_jyutping(self, chars: str, splitter: str = '-',
                     tone_marks: Optional[str] = 'numbers', convert: str = 'lower') -> str:
        """The Jyutping of chars, each reading chosen from its context."""
        return self.get_jyutpings(chars, splitter, tone_marks, convert, n=1)[0]

    def get_initial(self, char: str, full: bool = False) -> str:
        """First letter of the reading, upper-cased ('N' for 你).  With
        full=True the whole initial consonant ('NG' for 我, 'GW' for 廣), or
        '' for a syllable without one (屋 uk1, and the syllabic nasals 唔 m4,
        五 ng5).  Anything but a Chinese character is returned unchanged."""
        return self.get_initials(char, '', full)

    def get_initials(self, chars: str, splitter: str = '-', full: bool = False) -> str:
        """get_initial for every character, with readings chosen in context."""
        out = []
        for c, r in self.annotate(chars):
            if r is None:
                out.append(c)
            elif full:
                m = _INITIAL.match(r.lower())
                out.append(m.group(0).upper() if m and r.lower().rstrip('123456')
                           not in ('m', 'ng') else '')
            else:
                out.append(r[:1].upper())
        return splitter.join(out)

    # --- internals ---------------------------------------------------------

    def _canon(self, s: str) -> str:
        return ''.join(self._variants.get(c, c) for c in s)

    def _runs(self, text: str) -> List[List[int]]:
        """Positions of the Chinese characters of each run.  Anything else
        ends a run, except spaces and single line breaks between two
        characters (a blank line does end it).  A character missing from
        the data that has a set_jyutping reading is a run of its own."""
        runs: List[List[int]] = []
        run: List[int] = []
        newlines = 0
        for i, c in enumerate(text):
            if c in self._chars:
                run.append(i)
                newlines = 0
                continue
            if c in ' \t\r\n':      # TeX ends a line at LF, CR or CRLF
                newlines += c == '\n' or (c == '\r' and text[i + 1:i + 2] != '\n')
                if newlines < 2:
                    continue
            if run:
                runs.append(run)
                run = []
            if c in self._user_chars:   # not in the data: read without context
                runs.append([i])
            newlines = 0
        if run:
            runs.append(run)
        return runs

    def _key(self, run: str, canon: str, i: int, j: int) -> Optional[str]:
        """How the word run[i:j] is listed (as spelt, or with canonical
        characters), or None."""
        if run[i:j] in self._words:
            return run[i:j]
        return canon[i:j] if canon[i:j] in self._words else None

    def _segment_run(self, run: str) -> List[Segment]:
        """Split a run into the fewest words, then the fewest single
        characters, then the most usual words (the least total cost, from
        word frequencies); on a full tie the longer final word wins.  The
        count is 100000 per segment plus 1 per single character."""
        n, canon, words = len(run), self._canon(run), self._words
        cost, back = [(0, 0)] * (n + 1), [1] * (n + 1)
        for i in range(1, n + 1):
            c = run[i - 1]
            best = (cost[i - 1][0] + 100001,
                    cost[i - 1][1] + self._cost.get(c, self._cost.get(canon[i - 1], 0)))
            top = min(i, max(self._longest.get(run[i - 1], 0),
                             self._longest.get(canon[i - 1], 0)))
            for size in range(2, top + 1):
                key = self._key(run, canon, i - size, i)
                if key is None:
                    continue
                here = (cost[i - size][0] + 100000, cost[i - size][1] + self._cost.get(key, 0))
                if here <= best:
                    best, back[i] = here, size
            cost[i] = best
        bounds, j = [], n
        while j:
            bounds.append((j - back[j], j))
            j -= back[j]
        segments = []
        for i, j in reversed(bounds):
            text = run[i:j]
            if j - i > 1:
                key = text if text in words else canon[i:j]
                segments.append(Segment(text, words[key].split(),
                                        'u' if key in self._user_words else 'w'))
            elif text in self._user_chars:
                segments.append(Segment(text, [self._user_chars[text]], 'u'))
            else:
                default, _, polyphone = self._chars[text]
                reading = (self._next.get(run[i:i + 3]) or self._next.get(canon[i:i + 3])
                           or self._next.get(run[i:i + 2]) or self._next.get(canon[i:i + 2]))
                if reading is None:
                    reading = self._finals.get(text, default) if j == n else default
                segments.append(Segment(text, [reading], 'm' if polyphone else 's'))
        return segments

    def _readings(self, text: str) -> List[Optional[str]]:
        out: List[Optional[str]] = [None] * len(text)
        for run in self._runs(text):
            pos = iter(run)
            for seg in self._segment_run(''.join(text[i] for i in run)):
                for r in seg.readings:
                    out[next(pos)] = r
        return out
