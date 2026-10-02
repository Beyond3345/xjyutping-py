# xjyutping (Python)

Version 1.3.0 (2026-10-02). Versions follow
[Semantic Versioning](https://semver.org), and the history of the project is
kept in
[`CHANGELOG.md`](https://github.com/Beyond3345/xjyutping-py/blob/main/CHANGELOG.md).

## Overview

This project is a Python package that converts Traditional Chinese text to
Cantonese Jyutping (粵拼). It is aimed at developers and learners who need the
Cantonese pronunciation of a text, for example to add Jyutping to subtitles,
word lists or teaching material.

Pronunciation is determined by looking at the context and cross-referencing
it with a list of about 104 000 words, so 行 is read *hong4* in 銀行 but
*haang4* in 行路. The package is the Python version of the LaTeX package
[xjyutping](https://github.com/Beyond3345/xjyutping-tex) and gives the same
readings. It was inspired by [xpinyin](https://github.com/lxneng/xpinyin),
which converts Chinese characters to Mandarin pinyin, and its API follows
that of xpinyin.

## Installing

The package needs Python 3.8 or later and has no dependencies. To install it,
run,

```bash
pip install xjyutping
```

It can also be installed from GitHub with
`pip install git+https://github.com/Beyond3345/xjyutping-py`. For
development, run the following command, where the editable install needs pip
21.3 or later,

```bash
python3 -m pip install --upgrade pip && pip install -e '.[test]' && pytest tests
```

## Usage

The main method is `get_jyutping`, which returns the Jyutping of a text,

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

The `tone_marks` argument works with `get_jyutping`, `get_jyutpings` and
`annotate`, and it takes four values,

| `tone_marks` | 詩史試時市事 |
| --- | --- |
| `'numbers'` (default) | si1 si2 si3 si4 si5 si6 |
| `None` | si si si si si si |
| `'fancy'` | siˉ¹ siˊ² si˗₃ siˎ₄ siˏ₅ siˍ₆ |
| `'discord'` | siˉ¹ si⸍² si-₃ si⸜₄ si⸝₅ siˍ₆ |

The `'fancy'` and `'discord'` styles use the tone symbols of
[Visual Jyutping](https://github.com/VincentTam/visual-jyutping), taken from
its web and Discord versions. Any other value raises `ValueError`.

```pycon
>>> j.get_jyutping('行路', ' ', tone_marks='fancy')
'haangˎ₄ louˍ₆'
>>> Jyutping.decode_jyutping('hou2', 'fancy')
'houˊ²'
```

### Context and your own readings

The reading of each character is chosen in three steps. First, the text is
split into runs of Chinese characters. Then each run is split into the fewest
words from the word list, the more common words winning where two splits
have as many words, and each word takes its reading from the list. Lastly, a
character left on its own takes the reading you set, or otherwise the
reading given by the characters after it, its reading at the end of a run or
its default reading. Specifically, 呢 is the demonstrative *ni1* before a
classifier but the particle *ne1* elsewhere, while variant shapes such as
為/爲 and 裡/裏 find the same words.

```pycon
>>> j.get_jyutping('校長喺學校長大')
'haau6-zoeng2-hai2-hok6-haau6-zoeng2-daai6'
>>> j.get_jyutping('呢張床好平，好麻煩呢？', ' ')
'ni1 zoeng1 cong4 hou2 peng4 ， hou2 maa4 faan4 ne1 ？'
>>> j.get_jyutping('北京路步行街', ' ')
'bak1 ging1 lou6 bou6 hang4 gaai1'
>>> j.segment('佢當我係朋友')
[Segment(text='佢', readings=['keoi5'], type='s'), Segment(text='當', readings=['dong1'], type='m'), Segment(text='我', readings=['ngo5'], type='s'), Segment(text='係', readings=['hai6'], type='s'), Segment(text='朋友', readings=['pang4', 'jau5'], type='w')]
```

The `segment` method shows how a text was read, in the same way as the
`debug` option of the LaTeX package. Its types are `w` for a word from the
list, `u` for a reading you set, `m` for a guessed reading of a character
with several readings and `s` for a character with only one reading. Here 當
is guessed as *dong1* ("when"), while the sentence means "he treats me as a
friend" (*dong3*).

The `set_jyutping` method works like `\setjyutping` in LaTeX. A single
character gets a new default reading, while several characters, with one
syllable each, become a word, which also wins a tie between two ways of
splitting a run. A syllable count that does not match raises `ValueError`,
and the settings belong to the `Jyutping` instance.

```pycon
>>> j.set_jyutping('當我', 'dong3 ngo5')
>>> j.get_jyutping('佢當我係朋友')
'keoi5-dong3-ngo5-hai6-pang4-jau5'
>>> j.set_jyutping('當', 'dong3')
>>> j.get_jyutping('佢當佢係朋友')
'keoi5-dong3-keoi5-hai6-pang4-jau5'
```

### Combinations

The `get_jyutpings` method lists up to `n` (10 by default) combinations of
readings, with the reading in context first,

```pycon
>>> j.get_jyutpings('行')
['haang4', 'hang4', 'hong4', 'hong2', 'hang6']
>>> j.get_jyutpings('銀行', n=3)
['ngan4-hong4', 'ngan4-haang4', 'ngan4-hang4']
>>> j.get_jyutpings('行', tone_marks=None)
['haang', 'hang', 'hong']
```

### Initials

The `get_initial` and `get_initials` methods give the first letter of each
reading in capitals and leave other text unchanged. With `full=True` they
give the whole initial (`NG`, `GW`, `KW` ...), or an empty string for a
syllable without one, such as 屋 *uk1* or 唔 *m4*.

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

The data in `src/xjyutping/data/` (30 089 characters and about 104 000 words,
each with how often it is used) is generated by `tools/build-data.py` in
[xjyutping-tex](https://github.com/Beyond3345/xjyutping-tex), from the
sources credited below. Readings should therefore be fixed there, not in the
TSV files. Where rime-cantonese gives a word several readings, the data takes
the one that ToJyutping chooses, since its choices follow Hong Kong usage
(for example 公園 *gung1 jyun2*). Where two ways of splitting a run have as
many words and single characters, the more common words win, as counted in
the word-frequency list of rime-cantonese and in the transcripts of
WenetSpeech-Yue, and a few characters take their reading from the characters
after them (`next.tsv`), such as the demonstrative 呢 *ni1* before a
classifier.

We measured the accuracy on seven corpora. The Hong Kong Cantonese Corpus
(HKCanCor) is a corpus of conversation recorded in the 1990s whose 161 045
characters were annotated with Jyutping by hand. On the half of its files
that was kept out of the tuning, the package reads 95.6% of the characters
correctly (94.0% in 1.2.0) and 97.9% of the characters outside
sentence-final particles and interjections, while ToJyutping 3.2.0 reads
92.6% and 96.1%. On the particles of CantoMap, which were transcribed by ear,
it reads 97.5% (79.0% in 1.2.0, 83.0% for ToJyutping). On fresh sentences of
SpiCE, MagicHub and WenetSpeech-Yue, where the systems disagree, the reading
of xjyutping was judged right in 91.7% of the cases, against 62.4%
for ToJyutping. Part II, Section 10 of the LaTeX package's
[`CHANGELOG.md`](https://github.com/Beyond3345/xjyutping-tex/blob/main/CHANGELOG.md)
describes the tests.

## Testing

Running `pytest tests` runs the tests. One of them checks that the readings
match the debug log of the LaTeX package (`tests/parity_expected.txt`), which
`tests/parity.tex` regenerates.

## Acknowledgements and attributions

This project was inspired by [xpinyin](https://github.com/lxneng/xpinyin) by
Eric Lo ([lxneng](https://lxneng.com)), a Python package that converts
Chinese characters to pinyin, and its API is the model for this one. The
LaTeX version of xjyutping was in turn inspired by the LaTeX package
[xpinyin](https://ctan.org/pkg/xpinyin) by Qing Lee (李清).

The `'fancy'` and `'discord'` styles use the tone symbols of
[Visual Jyutping](https://github.com/VincentTam/visual-jyutping) by Vincent
Tam, which was itself inspired by the Visual Cantonese Fonts (粵語字體) by Jon
Chui / A3I Ltd. ([canto.hk](https://canto.hk),
[documentation](https://docs.visual-fonts.com),
[source](https://github.com/jkwchui/visual-fonts-starlight-docs)). We would
like to thank both of them.

We also thank the authors of the data sources,

- the Jyutping Workgroup of the Linguistic Society of Hong Kong (LSHK), for
  the *Cantonese Pronunciation List of Characters for Computers*
  (電腦用漢字粵語拼音表,
  [lshk-org/jyutping-table](https://github.com/lshk-org/jyutping-table),
  CC BY 4.0), together with Prof Lu Qin and Dr Cheung Kwan Hin of the Hong
  Kong Polytechnic University and Nathan Hammond, who are thanked there,
- the Cantonese Computational Linguistics Infrastructure Development
  Workgroup (CanCLID) and its contributors, for
  [rime-cantonese](https://github.com/rime/rime-cantonese) (粵語拼音輸入方案,
  CC BY 4.0), which gives the default readings and most of the words, and
  for [ToJyutping](https://github.com/CanCLID/ToJyutping) (BSD-2-Clause),
  whose word list chooses between rime's readings of a word and adds 512
  words,
- 石見田, for 粵音資料集叢 ([jyut.net](https://jyut.net/about), data at
  [jyutnet/cantonese-books-data](https://github.com/jyutnet/cantonese-books-data)),
  together with the authors and editors of the thirteen dictionaries it
  digitises, namely 廣州話正音字典 (2004), 廣州話標準音字彙 (1988), 粵語同音字典 (1974/1996),
  粵語查音識字字典 (1985), 同音字彙 (1971), 部身字典 (1967), *The Student's
  Cantonese-English Dictionary* (1947), 粵音韻彙 (1941), 道字典 (1941),
  道漢字音 (1939), 民眾識字粵語拼音字彙 (1931), 廣話國語一貫未定稿 (1916) and
  分部分音廣話九聲字宗 (1914),
- Aaron Tan, for [Jyut Dictionary](https://github.com/aaronhktan/jyut-dict),
  which distributes CC-Canto (© 2015–17 Pleco Inc.,
  [cantonese.org](https://cantonese.org), CC BY-SA 3.0) and the Cantonese
  readings for CC-CEDICT (© 2015 Pleco Software Inc., CC BY-SA 3.0), together
  with MDBG and the contributors of [CC-CEDICT](https://cc-cedict.org) and
- Carbo Kuo (BYVoid) and the contributors of OpenCC, for
  [OpenCC](https://github.com/BYVoid/OpenCC) (Apache-2.0), whose variant
  tables let variant shapes find the same words.

Lastly, we thank the authors of the corpora that we used to tune the package
and to measure its accuracy,

- Kang Kwong Luke, for the Hong Kong Cantonese Corpus (HKCanCor, CC BY 4.0),
  as distributed with [PyCantonese](https://github.com/jacksonllee/pycantonese),
- Grégoire Winterstein, Carmen Tang and Regine Lai, for
  [CantoMap](https://github.com/gwinterstein/CantoMap) (GPL-3.0),
- Khia A. Johnson, Molly Babel, Ivan Fong and Nancy Yiu, for SpiCE
  ([doi:10.5683/SP2/MJOXP3](https://doi.org/10.5683/SP2/MJOXP3), CC BY 4.0),
- the ASLP-lab, for [WenetSpeech-Yue](https://github.com/ASLP-lab/WenetSpeech-Yue)
  (CC BY-NC 4.0), whose transcripts also give the word frequencies,
- Beijing Magic Data Technology, for the Guangzhou Cantonese Conversational
  Speech Corpus of [MagicHub](https://magichub.com) and
- the contributors of the Cantonese Wikipedia.

## Licence

The code is released under the MIT licence
([`LICENSE`](https://github.com/Beyond3345/xjyutping-py/blob/main/LICENSE)),
and the tone symbols in `TONE_MARKS` come from Visual Jyutping (MIT). The data
files in `src/xjyutping/data/` are released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), since they
adapt the CC BY-SA 3.0 word lists above. The word list of ToJyutping is used
under the BSD 2-Clause License, whose notice is reproduced in `LICENSE`. The
readings of the 640 characters from 粵音資料集叢 come from data published
without a licence and are used with attribution. The word costs use counts
of the transcripts of WenetSpeech-Yue (CC BY-NC 4.0); no text of any corpus
is included.
