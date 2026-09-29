# xjyutping (Python)

Version 1.1.0 (2026-09-28). Versions follow
[Semantic Versioning 2.0.0](https://semver.org); the history, and handover
notes for maintainers, are in [`CHANGELOG.md`](https://github.com/Beyond3345/xjyutping-py/blob/main/CHANGELOG.md).

Translate traditional Chinese text to Cantonese Jyutping (粵拼), choosing each
reading from the words around it: 行 is *hong4* in 銀行 but *haang4* in 行路.

This is the Python port of the LaTeX package
[xjyutping](https://github.com/Beyond3345/xjyutping-tex), with the API of
[xpinyin](https://github.com/lxneng/xpinyin), the Python project that
inspired it (see the acknowledgements below). It
uses the same data and the same segmentation, so it gives the same readings
as the LaTeX package; a test checks this against the LaTeX package's debug
log.

## Install

Python 3.8 or later, no dependencies.

```bash
pip install git+https://github.com/Beyond3345/xjyutping-py
```

or, in a checkout of this repository, `pip install .`. For development
(editable installs need pip 21.3 or later):

```bash
python3 -m pip install --upgrade pip && pip install -e '.[test]' && pytest tests
```

## Usage

```pycon
>>> from xjyutping import Jyutping
>>> j = Jyutping()
>>> j.get_jyutping('我哋去銀行')          # default splitter is '-'
'ngo5-dei6-heoi3-ngan4-hong4'
>>> j.get_jyutping('行路返屋企', ' ')
'haang4 lou6 faan1 uk1 kei2'
>>> j.get_jyutping('香港', '')
'hoeng1gong2'
>>> j.get_jyutping('香港', convert='capitalize')    # or 'upper'; default 'lower'
'Hoeng1-Gong2'
>>> j.get_jyutping('Apple發布iOS7')      # other text is kept as it is
'Apple-faat3-bou3-iOS7'
>>> j.get_jyutping('你好 世界')           # spaces between characters are dropped
'nei5-hou2-sai3-gaai3'
>>> j.annotate('銀行 ATM')              # one pair per input character
[('銀', 'ngan4'), ('行', 'hong4'), (' ', None), ('A', None), ('T', None), ('M', None)]
```

### Tone styles

`tone_marks` works for `get_jyutping`, `get_jyutpings` and `annotate`:

| `tone_marks` | 詩史試時市事 |
| --- | --- |
| `'numbers'` (default) | si1 si2 si3 si4 si5 si6 |
| `None` | si si si si si si |
| `'fancy'` | siˉ¹ siˊ² si˗₃ siˎ₄ siˏ₅ siˍ₆ |
| `'discord'` | siˉ¹ si⸍² si-₃ si⸜₄ si⸝₅ siˍ₆ |

`'fancy'` and `'discord'` are the tone symbols of
[Visual Jyutping](https://github.com/VincentTam/visual-jyutping) (its web and
Discord maps): a contour mark for the pitch and the tone number, superscript
for the high tones 1 and 2, subscript for the others; the LaTeX package's
`fancy` option draws the same marks. Any other value raises `ValueError`.

```pycon
>>> j.get_jyutping('行路', ' ', tone_marks='fancy')
'haangˎ₄ louˍ₆'
>>> Jyutping.decode_jyutping('hou2', 'fancy')
'houˊ²'
```

### Context and your own readings

A text is split into runs of Chinese characters (anything else ends a run,
except spaces and single line breaks between two characters; a blank line
does end it; LF, CR and CRLF all end a line, as in TeX). Each run is split
into the fewest words from a list of about 104 000, then the fewest single
characters; on a tie the longer final word wins. A word takes its reading
from the list; a character on its own takes your reading if you set one,
else its default. One character, 呢, reads differently alone at the end of
a run (*ni1* in 呢張床 but *ne1* in 好麻煩呢？). Variant shapes (為/爲,
裡/裏, 説/說 ...) find the same words.

```pycon
>>> j.get_jyutping('校長喺學校長大')
'haau6-zoeng2-hai2-hok6-haau6-zoeng2-daai6'
>>> j.get_jyutping('呢張床好平，好麻煩呢？', ' ')
'ni1 zoeng1 cong4 hou2 peng4 ， hou2 maa4 faan4 ne1 ？'
>>> j.segment('佢重話聽日嚟')
[Segment(text='佢', readings=['keoi5'], type='s'), Segment(text='重', readings=['cung5'], type='m'), Segment(text='話', readings=['waa6'], type='s'), Segment(text='聽日', readings=['ting1', 'jat6'], type='w'), Segment(text='嚟', readings=['lai4'], type='m')]
```

`segment` shows how a text was read, like the LaTeX package's `debug`
option. Types: `w` word from the list, `u` your setting, `m` a character with
several common readings whose reading was guessed, `s` a character with one
common reading.

`set_jyutping` is `\setjyutping`: one character gets a new default reading;
several characters (one syllable each, separated by spaces) become a word
that beats the word list. Whitespace in the text is ignored. A syllable
count that differs from the character count raises `ValueError`. A
character missing from the data gets your reading too, without context (it
still ends a run). Settings belong to the `Jyutping` instance.

```pycon
>>> j.set_jyutping('重話', 'zung6 waa6')
>>> j.get_jyutping('佢重話聽日嚟')
'keoi5-zung6-waa6-ting1-jat6-lai4'
>>> j.set_jyutping('重', 'zung6')
>>> j.get_jyutping('佢重未嚟')
'keoi5-zung6-mei6-lai4'
```

### Combinations

`get_jyutpings` lists up to `n` (default 10) combinations of readings: the
reading in context first for each character, then its other readings.

```pycon
>>> j.get_jyutpings('行')
['haang4', 'hang4', 'hong4', 'hong2', 'hang6']
>>> j.get_jyutpings('銀行', n=3)
['ngan4-hong4', 'ngan4-haang4', 'ngan4-hang4']
>>> j.get_jyutpings('行', tone_marks=None)
['haang', 'hang', 'hong']
```

### Initials

`get_initial` / `get_initials` give the first letter of each reading,
upper-cased (readings chosen in context); anything but a Chinese character
is returned unchanged. With `full=True` they give the whole initial
consonant (`NG`, `GW`, `KW` ...), and an empty string for a syllable that has
none: a vowel-initial syllable (屋 *uk1*) or a syllabic nasal (唔 *m4*,
五 *ng5*).

```pycon
>>> j.get_initials('我哋去廣州')
'N-D-H-G-Z'
>>> j.get_initials('我哋去廣州', full=True)
'NG-D-H-GW-Z'
>>> j.get_initials('唔五屋'), j.get_initials('唔五屋', full=True)
('M-N-U', '--')
```

## API

| | |
| --- | --- |
| `Jyutping(data_dir=None)` | Loads the data (from the package unless `data_dir` is given). |
| `get_jyutping(chars, splitter='-', tone_marks='numbers', convert='lower')` | Jyutping of a text. |
| `get_jyutpings(chars, splitter='-', tone_marks='numbers', convert='lower', n=10)` | Combinations of readings. |
| `annotate(text, tone_marks='numbers')` | `[(char, reading or None), ...]`, one per character. |
| `segment(text)` | `[Segment(text, readings, type), ...]` for the Chinese text. |
| `set_jyutping(text, reading)` | Your reading for a character or a word. |
| `get_initial(char, full=False)`, `get_initials(chars, splitter='-', full=False)` | Initials. |
| `Jyutping.decode_jyutping(syllable, tone_marks)`, `Jyutping.convert_jyutping(syllable, convert)` | Format one syllable. |

## Data

`src/xjyutping/data/*.tsv` (30 089 characters, about 104 000 words) are
generated, together with the LaTeX package's data, by `tools/build-data.py`
of [xjyutping-tex](https://github.com/Beyond3345/xjyutping-tex); edit the
hand-checked tables there and rebuild, never the TSV files. The sources are
the LSHK *Cantonese Pronunciation List of Characters for Computers*
(粵拼表), rime-cantonese (default readings and the main word list), CC-Canto
and the Cantonese readings of CC-CEDICT as distributed with Jyut Dictionary
(2 291 more words), OpenCC's variant tables and, for 640 characters the
others lack, the book data of 粵音資料集叢 (see the acknowledgements
below). rime-cantonese is
authoritative: the other word lists only add words that it does not have.

The files are `chars.tsv` (character, default reading, other readings,
polyphone flag), `finals.tsv` (reading at the end of a run), `variants.tsv`
(variant, canonical character) and `words.tsv` (word, readings).

## Tests

`tests/test_xjyutping.py` (pytest). `test_parity_with_tex_package` compares
every segment, reading and type for `tests/parity_corpus.txt` with
`tests/parity_expected.txt`, the debug log of the LaTeX package for the same
text; `tests/parity.tex` regenerates that log (with XeLaTeX or LuaLaTeX) when
the package or its data change.

## Acknowledgements and attributions

**Inspiration.** This project was inspired by
[xpinyin](https://github.com/lxneng/xpinyin), the Python package by Eric Lo
([lxneng](https://lxneng.com)) that turns Chinese characters into Hanyu
Pinyin: its API (`get_pinyin`, `get_pinyins`, `get_initial(s)`, splitters,
tone styles, conversions) is the model for this one. The LaTeX version,
[xjyutping](https://github.com/Beyond3345/xjyutping-tex), was in turn
inspired by the LaTeX package [xpinyin](https://ctan.org/pkg/xpinyin) by Qing
Lee (李清).

**Tone styles.** The `'fancy'` and `'discord'` styles were inspired by, and
use the symbols of, [Visual Jyutping](https://github.com/VincentTam/visual-jyutping)
by Vincent Tam, itself inspired by the Visual Cantonese Fonts (粵語字體) by Jon
Chui / A3I Ltd.: [canto.hk](https://canto.hk), with documentation at
[docs.visual-fonts.com](https://docs.visual-fonts.com)
([source](https://github.com/jkwchui/visual-fonts-starlight-docs)). Thank you
both.

**Readings and vocabulary.** Many thanks to the authors of every source the
data is built from:

* the *Cantonese Pronunciation List of Characters for Computers*
  (電腦用漢字粵語拼音表), maintained by the Jyutping Workgroup of the
  Linguistic Society of Hong Kong
  ([lshk-org/jyutping-table](https://github.com/lshk-org/jyutping-table),
  CC BY 4.0), with the thanks given there to Prof Lu Qin and Dr Cheung Kwan
  Hin of the Hong Kong Polytechnic University and to Nathan Hammond;
* [rime-cantonese](https://github.com/rime/rime-cantonese) (粵語拼音輸入方案)
  by the Cantonese Computational Linguistics Infrastructure Development
  Workgroup (CanCLID) and its contributors (CC BY 4.0), which gives the
  default readings and most of the words;
* 石見田 and the 粵音資料集叢 ([jyut.net](https://jyut.net/about), data at
  [jyutnet/cantonese-books-data](https://github.com/jyutnet/cantonese-books-data)),
  whose digitised dictionaries give the readings of 640 characters: 廣州話正音字典
  (2004), 廣州話標準音字彙 (1988), 粵語同音字典 (1974/1996), 粵語查音識字字典
  (1985), 同音字彙 (1971), 部身字典 (1967), *The Student's Cantonese-English
  Dictionary* (1947), 粵音韻彙 (1941), 道字典 (1941), 道漢字音 (1939),
  民眾識字粵語拼音字彙 (1931), 廣話國語一貫未定稿 (1916) and
  分部分音廣話九聲字宗 (1914); and the authors and editors of those books;
* [Jyut Dictionary](https://github.com/aaronhktan/jyut-dict) (jyut-dict) by
  Aaron Tan, whose `src/dictionaries` distributes the two word lists used
  here: CC-Canto (© 2015–17 Pleco Inc., [cantonese.org](https://cantonese.org),
  CC BY-SA 3.0) and the Cantonese readings for CC-CEDICT (© 2015 Pleco
  Software Inc., CC BY-SA 3.0), which give Cantonese readings to the words of
  [CC-CEDICT](https://cc-cedict.org) by MDBG and its contributors;
* [OpenCC](https://github.com/BYVoid/OpenCC) by Carbo Kuo (BYVoid) and its
  contributors (Apache-2.0), whose Hong Kong and Taiwan variant tables let
  variant shapes find the same words.

## Licence

The code is under the MIT licence ([`LICENSE`](https://github.com/Beyond3345/xjyutping-py/blob/main/LICENSE)); the tone symbols of
`TONE_MARKS` come from Visual Jyutping (MIT). The data files in
`src/xjyutping/data/` are distributed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): they adapt
the CC BY-SA 3.0 word lists of CC-Canto and the CC-CEDICT Cantonese readings,
together with material under CC BY 4.0 (LSHK, rime-cantonese) and Apache-2.0
(the OpenCC variant map), all credited above. The readings of the 640
characters taken from 粵音資料集叢 come from data published without a licence
statement and are used with attribution.
