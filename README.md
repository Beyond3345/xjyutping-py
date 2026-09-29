# xjyutping (Python)

Version 1.1.0 (2026-09-28). Versions follow
[Semantic Versioning](https://semver.org), and the history is in
[`CHANGELOG.md`](https://github.com/Beyond3345/xjyutping-py/blob/main/CHANGELOG.md).

xjyutping converts Traditional Chinese text to Cantonese Jyutping (粵拼).
Pronunciation is determined by looking at the context and cross-referencing
it with a list of about 104 000 words, so 行 is *hong4* in 銀行 but *haang4*
in 行路. It is the Python version of the LaTeX package
[xjyutping](https://github.com/Beyond3345/xjyutping-tex) and gives the same
readings. It was inspired by [xpinyin](https://github.com/lxneng/xpinyin),
which converts Chinese characters to Mandarin pinyin, and follows its API.

## Install

Python 3.8 or later, no dependencies.

```bash
pip install xjyutping
```

or from GitHub with `pip install git+https://github.com/Beyond3345/xjyutping-py`.
For development (editable installs need pip 21.3 or later):

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

`tone_marks` works with `get_jyutping`, `get_jyutpings` and `annotate`:

| `tone_marks` | 詩史試時市事 |
| --- | --- |
| `'numbers'` (default) | si1 si2 si3 si4 si5 si6 |
| `None` | si si si si si si |
| `'fancy'` | siˉ¹ siˊ² si˗₃ siˎ₄ siˏ₅ siˍ₆ |
| `'discord'` | siˉ¹ si⸍² si-₃ si⸜₄ si⸝₅ siˍ₆ |

`'fancy'` and `'discord'` use the tone symbols of
[Visual Jyutping](https://github.com/VincentTam/visual-jyutping), from its web
and Discord versions. Any other value raises `ValueError`.

```pycon
>>> j.get_jyutping('行路', ' ', tone_marks='fancy')
'haangˎ₄ louˍ₆'
>>> Jyutping.decode_jyutping('hou2', 'fancy')
'houˊ²'
```

### Context and your own readings

Text is split into runs of Chinese characters, and each run is split into
the fewest words from the word list. A word takes its reading from the list,
and a character on its own takes your reading or else its default. 呢 reads
*ni1* inside a run but *ne1* at its end. Variant shapes such as 為/爲 and
裡/裏 find the same words.

```pycon
>>> j.get_jyutping('校長喺學校長大')
'haau6-zoeng2-hai2-hok6-haau6-zoeng2-daai6'
>>> j.get_jyutping('呢張床好平，好麻煩呢？', ' ')
'ni1 zoeng1 cong4 hou2 peng4 ， hou2 maa4 faan4 ne1 ？'
>>> j.segment('佢重話聽日嚟')
[Segment(text='佢', readings=['keoi5'], type='s'), Segment(text='重', readings=['cung5'], type='m'), Segment(text='話', readings=['waa6'], type='s'), Segment(text='聽日', readings=['ting1', 'jat6'], type='w'), Segment(text='嚟', readings=['lai4'], type='m')]
```

`segment` shows how a text was read, like the LaTeX package's `debug`
option. The types are `w` for a word from the list, `u` for your setting, `m`
for a guessed reading of a character with several, and `s` for a character
with one reading.

`set_jyutping` works like `\setjyutping` in LaTeX. One character gets a new
default reading, and several characters (one syllable each) become a word. A
syllable count that doesn't match raises `ValueError`. Settings belong to the
`Jyutping` instance.

```pycon
>>> j.set_jyutping('重話', 'zung6 waa6')
>>> j.get_jyutping('佢重話聽日嚟')
'keoi5-zung6-waa6-ting1-jat6-lai4'
>>> j.set_jyutping('重', 'zung6')
>>> j.get_jyutping('佢重未嚟')
'keoi5-zung6-mei6-lai4'
```

### Combinations

`get_jyutpings` lists up to `n` (default 10) combinations of readings, with
the reading in context first.

```pycon
>>> j.get_jyutpings('行')
['haang4', 'hang4', 'hong4', 'hong2', 'hang6']
>>> j.get_jyutpings('銀行', n=3)
['ngan4-hong4', 'ngan4-haang4', 'ngan4-hang4']
>>> j.get_jyutpings('行', tone_marks=None)
['haang', 'hang', 'hong']
```

### Initials

`get_initial` and `get_initials` give the first letter of each reading in
capitals, and leave other text unchanged. With `full=True` they give the
whole initial (`NG`, `GW`, `KW` ...), or an empty string for a syllable
without one, such as 屋 *uk1* or 唔 *m4*.

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

The data in `src/xjyutping/data/` (30 089 characters, about 104 000 words) is
generated by `tools/build-data.py` in
[xjyutping-tex](https://github.com/Beyond3345/xjyutping-tex), from the
sources credited below. Fix readings there, not in the TSV files.

## Tests

`pytest tests` runs the tests. One of them checks that the readings match
the LaTeX package's debug log (`tests/parity_expected.txt`), which
`tests/parity.tex` regenerates.

## Acknowledgements and attributions

This project was inspired by [xpinyin](https://github.com/lxneng/xpinyin) by
Eric Lo ([lxneng](https://lxneng.com)), a Python package that converts
Chinese characters to pinyin. Its API is the model for this one. The LaTeX
version of xjyutping was inspired by the LaTeX package
[xpinyin](https://ctan.org/pkg/xpinyin) by Qing Lee (李清).

The `'fancy'` and `'discord'` styles use the tone symbols of
[Visual Jyutping](https://github.com/VincentTam/visual-jyutping) by Vincent
Tam, which was itself inspired by the Visual Cantonese Fonts (粵語字體) by Jon
Chui / A3I Ltd. ([canto.hk](https://canto.hk),
[documentation](https://docs.visual-fonts.com),
[source](https://github.com/jkwchui/visual-fonts-starlight-docs)). Thank you
both.

Thanks also to the authors of the data sources:

* the Jyutping Workgroup of the Linguistic Society of Hong Kong, for the
  *Cantonese Pronunciation List of Characters for Computers*
  (電腦用漢字粵語拼音表,
  [lshk-org/jyutping-table](https://github.com/lshk-org/jyutping-table),
  CC BY 4.0), and to Prof Lu Qin and Dr Cheung Kwan Hin of the Hong Kong
  Polytechnic University and Nathan Hammond, who are thanked there;
* the Cantonese Computational Linguistics Infrastructure Development
  Workgroup (CanCLID) and contributors, for
  [rime-cantonese](https://github.com/rime/rime-cantonese) (粵語拼音輸入方案,
  CC BY 4.0), which gives the default readings and most of the words;
* 石見田, for 粵音資料集叢 ([jyut.net](https://jyut.net/about), data at
  [jyutnet/cantonese-books-data](https://github.com/jyutnet/cantonese-books-data)),
  and the authors and editors of the dictionaries it digitises: 廣州話正音字典
  (2004), 廣州話標準音字彙 (1988), 粵語同音字典 (1974/1996), 粵語查音識字字典
  (1985), 同音字彙 (1971), 部身字典 (1967), *The Student's Cantonese-English
  Dictionary* (1947), 粵音韻彙 (1941), 道字典 (1941), 道漢字音 (1939),
  民眾識字粵語拼音字彙 (1931), 廣話國語一貫未定稿 (1916) and
  分部分音廣話九聲字宗 (1914);
* Aaron Tan, for [Jyut Dictionary](https://github.com/aaronhktan/jyut-dict),
  which distributes CC-Canto (© 2015–17 Pleco Inc.,
  [cantonese.org](https://cantonese.org), CC BY-SA 3.0) and the Cantonese
  readings for CC-CEDICT (© 2015 Pleco Software Inc., CC BY-SA 3.0), and MDBG
  and the contributors of [CC-CEDICT](https://cc-cedict.org);
* Carbo Kuo (BYVoid) and contributors, for
  [OpenCC](https://github.com/BYVoid/OpenCC) (Apache-2.0), whose variant
  tables let variant shapes find the same words.

## Licence

The code is under the MIT licence
([`LICENSE`](https://github.com/Beyond3345/xjyutping-py/blob/main/LICENSE)),
and the tone symbols in `TONE_MARKS` come from Visual Jyutping (MIT). The data
files in `src/xjyutping/data/` are under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), because they
adapt the CC BY-SA 3.0 word lists above. The readings of the 640 characters
from 粵音資料集叢 come from data published without a licence and are used with
attribution.
