# xjyutping (Python)

Version 1.0.0 (2026-09-28). Versions follow
[Semantic Versioning 2.0.0](https://semver.org); the history is in
[`../CHANGELOG.md`](../CHANGELOG.md).

Translate traditional Chinese text to Cantonese Jyutping (粵拼), choosing each
reading from the words around it: 行 is *hong4* in 銀行 but *haang4* in 行路.

This is the Python port of the `xjyutping` LaTeX package (in `../xjyutping-tex`),
with the API of [xpinyin](https://github.com/lxneng/xpinyin). It uses the same
data and the same segmentation, so it gives the same readings as the LaTeX
package. A test checks this against the TeX package's debug log.

## Install

Python 3.8 or later, no dependencies.

```bash
pip install ./xjyutping-py        # from the repository root

# development (editable installs need pip 21.3 or later)
python3 -m pip install --upgrade pip
pip install -e './xjyutping-py[test]' && pytest xjyutping-py/tests
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
for the high tones 1 and 2, subscript for the others. Any other value raises
`ValueError`.

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
into the fewest words from a list of about 100 000, then the fewest single
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

`src/xjyutping/data/*.tsv` are generated, together with the LaTeX package's
`.def` files, by `python3 tools/build-data.py` at the repository root from:

* the LSHK *Cantonese Pronunciation List of Characters for Computers*
  (粵拼表), CC BY 4.0;
* rime-cantonese `jyut6ping3.chars` and `jyut6ping3.words`, CC BY 4.0;
* OpenCC `HKVariants.txt` and `TWVariants.txt`, Apache-2.0.

Hand-checked corrections live in `tools/build-data.py`; edit them there and
rerun the script, never the TSV files. The files are `chars.tsv` (character,
default reading, other readings, polyphone flag), `finals.tsv` (reading at
the end of a run), `variants.tsv` (variant, canonical character) and
`words.tsv` (word, readings).

## Tests

`tests/test_xjyutping.py` (pytest). `test_parity_with_tex_package` compares
every segment, reading and type for `tests/parity_corpus.txt` with
`tests/parity_expected.txt`, the debug log of the LaTeX package for the same
text; `tests/parity.tex` regenerates that log when the package or its data
change.

## Licence

The code is under the MIT licence (`LICENSE`). The data files carry the
licences of their sources (CC BY 4.0 for the readings, Apache-2.0 for the
variant map); the tone symbols come from Visual Jyutping (MIT).
