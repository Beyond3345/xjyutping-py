# Changelog

This file records all notable changes to xjyutping, the Python package. Its
format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
and its versions follow
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (SemVer).

This package is the Python port of the LaTeX package
[xjyutping](https://github.com/Beyond3345/xjyutping-tex), which has its own
version numbers and its own changelog. Beyond the LaTeX releases, that
changelog holds the full history of how both packages were built, including
the review rounds whose results this package inherits through the shared
data. This file, on the other hand, has the Python releases and the handover
notes for the Python side.

The version number is written in three places, which are `version` in
`pyproject.toml`, `__version__` in `src/xjyutping/__init__.py` and
`README.md`. The test `test_version` checks that the first two agree. For
every release we update all three and add an entry to Part I.

---

# Part I: Releases

## [Unreleased]

There are no entries yet. Add them here under `### Added`, `### Changed`,
`### Fixed` and so on.

## [1.3.0] - 2026-10-02

### Added

- Word frequencies. `words.tsv` and `chars.tsv` carry a cost, and where two
  ways of splitting a run have as many words and single characters, the one
  of least total cost (the more common words) wins, rather than the one with
  the longer final word (步行|街, not 步|行街). A word set with `set_jyutping`
  has cost 0, so it wins such a tie.
- `next.tsv`, the reading of a character standing alone before the one or
  two characters given, which `segment` checks before the run-final reading
  and the default. It holds the demonstrative 呢 and 哩 before a classifier
  (呢間 *ni1*) and 咁 *gam2* before a particle or a pronoun.
- `test_corpus_tuned_readings` and `test_frequency_tie_break`.

### Changed

- The data of xjyutping-tex 1.5.0, tuned on HKCanCor, CantoMap, SpiCE,
  WenetSpeech-Yue, MagicHub and the Cantonese Wikipedia. The particles follow
  present-day Hong Kong usage (呢 alone *ne1*, 咯 *lo3*, 哦 *o6*, 你做乜啊
  *aa3*), characters that are mostly read otherwise alone have new defaults
  (重 *zung6*, 下 *haa5*, 名 *meng2*), and about 200 words were corrected or
  added.
- `tests/parity_expected.txt` was regenerated from xjyutping-tex 1.5.0.

Overall, the share of the characters of the held-out half of HKCanCor that
the package reads correctly rises from 94.0% to 95.6%, and the share of the
particles of CantoMap from 79.0% to 97.5%.

## [1.2.0] - 2026-09-29

### Added

- The data of xjyutping-tex 1.4.0, which learns from ToJyutping (version
  3.2.0, by CanCLID, BSD-2-Clause). Where rime-cantonese gives a word several
  readings, the package now takes the one that ToJyutping chooses, such as 公園
  *gung1 jyun2*, 郵局 *jau4 guk2* and 請假 *ceng2 gaa3*, and 494 words of
  ToJyutping that rime lacks are added.
- `test_tojyutping_readings`, which checks 揾, 都會, 呢就, the new particle
  defaults and the words that ToJyutping decides.
- The README reports the accuracy measured against the Hong Kong Cantonese
  Corpus (HKCanCor), and `LICENSE` reproduces the BSD notice of ToJyutping.

### Changed

- The particles 囖, 嚹, 㗎 and 嘞 now default to *lo1*, *laa3*, *gaa3* and
  *laak3*.
- `tests/parity_expected.txt` was regenerated from xjyutping-tex 1.4.0, with
  two changed readings, 價錢 *cin4* and 便宜 *pin4 ji2*.

### Fixed

- 揾 now reads *wan2* (it is used for 搵), 都會 in 我哋都會去 reads *dou1 wui5*
  while 大都會 keeps *wui6*, and 係呢 reads *hai6 ne1*.

Overall, the share of the characters of HKCanCor that the package reads
correctly rises from 92.1% to 94.1%.

## [1.1.0] - 2026-09-28

### Added

- More vocabulary, from the data of xjyutping-tex 1.2.0. Specifically, the
  data now includes,
  - 2,291 words from CC-Canto and the Cantonese readings of CC-CEDICT, as
    distributed with Jyut Dictionary, which are added only where they change
    a reading and pass consistency checks against rime-cantonese (480 more
    were excluded by hand), and
  - 640 characters that the other sources lack, with readings from the book
    data of 粵音資料集叢 (jyutnet/cantonese-books-data, by 石見田).

  While nothing got worse on the corpora audited earlier, 24 readings
  improved and 3 changed neutrally on new test sentences (see the LaTeX
  package's changelog, Part II, Section 7.4).
- `test_added_vocabulary`, which checks new words, the words that must not
  capture their neighbours, the two hand fixes and a book character.
- A README section, "Acknowledgements and attributions", which covers,
  - the inspiration, [xpinyin](https://github.com/lxneng/xpinyin) by Eric Lo
    ([lxneng](https://lxneng.com)), whose API this package follows,
  - Visual Jyutping and the Visual Cantonese Fonts, which inspired the
    `fancy` and `discord` styles, and
  - every data source (LSHK, rime-cantonese, 粵音資料集叢, OpenCC and Jyut
    Dictionary with CC-Canto, the CC-CEDICT readings and CC-CEDICT).
- This `CHANGELOG.md` and a `.gitignore`. Up to 1.0.0 both packages shared
  one changelog in the folder that held them, and that history is kept in
  the changelog of xjyutping-tex.

### Changed

- The readings now follow xjyutping-tex 1.2.0. Examples of the changed
  readings are 機長 zoeng2, 營業額 ngaak2, 自由行 hang4, 研討會 wui2,
  消防隊 deoi2, 冠狀病毒 gun1 and 智能卡 kaat1. Further, 化合物 is now read
  faa3 hap6 mat6 and 會否 wui5 fau2.
- The data files in `src/xjyutping/data/` are now licensed under
  CC BY-SA 4.0, whereas before this they carried CC BY 4.0. This is due to
  the added word lists, which are under CC BY-SA 3.0, a share-alike licence.
  `LICENSE` lists every source, and the code stays under the MIT licence.
- `tests/parity.tex` now compiles with XeLaTeX or LuaLaTeX.
- `tests/parity_expected.txt` was regenerated from xjyutping-tex 1.2.0. Only
  one line changed, since 隨着 is now one word, with the same readings.
- The README is shorter, covers installing from PyPI or GitHub and links to
  the LaTeX package's repository. The PyPI summary is now "Convert
  Traditional Chinese text to Cantonese Jyutping (粵拼), with pronunciation
  chosen from context".
- We prepared the packaging for PyPI. `pyproject.toml` declares the licence
  as the SPDX expression `MIT AND CC-BY-SA-4.0` with `license-files`, and
  since this follows PEP 639, building the package needs setuptools 77 or
  later. It also has keywords, classifiers and the project URLs (for the
  repository, issues, changelog and the LaTeX package). `MANIFEST.in` adds
  `CHANGELOG.md` and the parity files to the sdist, and the sdist and wheel
  pass `twine check`.

## [1.0.0] - 2026-09-28

### Added

- The first release of the Python package `xjyutping`, which ports the LaTeX
  package to Python with the API of
  [xpinyin](https://github.com/lxneng/xpinyin). It needs Python 3.8 or later
  and has no dependencies. The class `Jyutping(data_dir=None)` has the
  methods,
  - `get_jyutping(chars, splitter='-', tone_marks='numbers', convert='lower')`,
  - `get_jyutpings(chars, splitter, tone_marks, convert, n=10)`, which gives
    the reading in context first and then the other readings,
  - `annotate(text, tone_marks)`, which gives one `(char, reading or None)`
    pair per input character,
  - `segment(text)`, which gives `Segment(text, readings, type)` with the
    types w/u/m/s of the TeX debug log,
  - `set_jyutping(text, reading)`, the equivalent of `\setjyutping`,
  - `get_initial(char, full=False)`,
  - `get_initials(chars, splitter, full)` and
  - the static methods `decode_jyutping` and `convert_jyutping`.
- The tone styles `'numbers'` (the default), `None`, `'fancy'` and
  `'discord'`. The last two use the exact code points of the web and Discord
  tone maps of Visual Jyutping, which are ˉ¹ ˊ² ˗₃ ˎ₄ ˏ₅ ˍ₆ and
  ˉ¹ ⸍² -₃ ⸜₄ ⸝₅ ˍ₆ respectively.
- The package gives the same readings as xjyutping-tex 1.1.0, since it uses
  the same data (`src/xjyutping/data/*.tsv`, generated by that package's
  `tools/build-data.py`) and the same run splitting, segmentation, variant
  folding, run-final readings and user overrides.
- 38 pytest tests, including a parity test against a frozen TeX debug log
  (`tests/parity.tex`, `parity_corpus.txt` and `parity_expected.txt`). The
  log holds 109 runs, with no mismatches.
- The code is under the MIT licence, while the data carried CC BY 4.0 (LSHK
  and rime-cantonese) and Apache-2.0 (OpenCC).

---

# Part II: Handover notes

## 0. Start here

The table below lists where things are.

| Path | What it is |
| --- | --- |
| `src/xjyutping/__init__.py` | The whole package: `Jyutping`, `Segment`, `TONE_MARKS`. |
| `src/xjyutping/data/*.tsv` | Generated data (see below); never edit by hand. |
| `tests/test_xjyutping.py` | pytest suite (40 tests). |
| `tests/parity_corpus.txt`, `parity_expected.txt`, `parity.tex` | The parity test with the LaTeX package: the corpus, the frozen TeX debug log, and the document that regenerates the log. |
| `pyproject.toml`, `MANIFEST.in` | Packaging (setuptools; the TSV files are package data; the sdist includes the parity files). |
| `README.md`, `LICENSE`, `CHANGELOG.md` | Documentation, licences (code MIT, data CC BY-SA 4.0), this file. |

The data is generated by `tools/build-data.py` in
[xjyutping-tex](https://github.com/Beyond3345/xjyutping-tex), together with
the LaTeX package's `.def` files. The script writes the data here when this
repository sits next to xjyutping-tex, or when it is run with
`--py-data DIR`. The files are,

- `chars.tsv`, which gives each character with its default reading, its
  other readings, a polyphone flag and (since 1.3.0) its cost,
- `finals.tsv`, which gives the reading at the end of a run,
- `next.tsv` (since 1.3.0), which gives the reading of a character standing
  alone before the one or two characters that follow it in the pattern,
- `variants.tsv`, which maps each variant to its canonical character and
- `words.tsv`, which gives each word with its readings and (since 1.3.0) its
  cost.

That repository's README and changelog describe the sources and every rule
for choosing readings.

Any change must keep these invariants.

1. The port must give the same readings as the LaTeX package.
   `test_parity_with_tex_package` compares every segment, reading and type of
   `tests/parity_corpus.txt` with the LaTeX package's debug log. When the
   data or the segmentation changes on purpose, regenerate
   `parity_expected.txt` with these steps,
   1. Compile `tests/parity.tex` with
      `TEXINPUTS=<xjyutping-tex>: LUAINPUTS=<xjyutping-tex>:` and
      `max_print_line=10000`
   2. Copy the `xjyutping>` lines into `parity_expected.txt`
   3. Check the diff by hand
2. Reading fixes belong in xjyutping-tex's `tools/build-data.py`, never in
   the TSV files or the code.
3. The algorithm mirrors the TeX package (Section 2), so a change on one side
   needs the same change on the other.
4. The code must stay compatible with Python 3.8. Hence it must not use
   `match`, `X | Y` unions evaluated at runtime or the string methods added
   in Python 3.9 and later.
5. Versions follow SemVer, which here means raising,
   - MAJOR for an incompatible change of the API (a method, argument or
     return value),
   - MINOR for a backward-compatible feature or for new vocabulary (as in
     1.1.0) and
   - PATCH for bug fixes and reading corrections.

To install the package and run the tests, use,

```bash
python3 -m pip install --upgrade pip && pip install -e '.[test]' && pytest tests
```

To run the tests without installing the package, use
`PYTHONPATH=src python3 -m pytest tests` instead. All tests must pass,
including `test_parity_with_tex_package`. To check a release, build the sdist
and wheel and run the tests from the extracted sdist.

## 1. How the port was built (with xjyutping-tex 1.1.0)

An agent wrote the port against a frozen copy of the LaTeX package 1.0.0. It
took the API of xpinyin and reproduced the algorithm of the LaTeX package,
specifically its runs, its segmentation by dynamic programming, its word and
character lookup and its user settings. The parity with TeX was then checked
on a 668-character corpus, which gave 0 mismatches.

Three independent reviewers then checked the port, each from one of these
angles,

- the reading parity with TeX, on a new 1 021-character corpus, where 119
  runs were compared line for line,
- the API, packaging and documentation, where the README examples were run
  as doctests and the contents of the wheel and the sdist were checked, and
- the edge cases and tone styles.

Every finding was reproduced before it was fixed. The porting agent's own 35
tests had all passed.

- P-1 (reported by all three reviewers). A lone carriage return (CR) was not
  counted as a line end, so `'\r\r'`, which TeX reads as a blank line, did
  not end a run, and this changed the segmentation and the run-final reading
  of 呢. `_runs` now counts `\n`, and `\r` not followed by `\n`, as line
  ends. The test `test_runs_cr_line_ends` covers this, with expected values
  taken from a TeX log.
- P-2. The sdist lacked the parity files, so its own test suite failed, with
  FileNotFoundError in 2 tests. `MANIFEST.in` now includes `tests/*.txt` and
  `*.tex`.
- P-3. The editable install in the README failed with pip 21.2.4, since
  editable installs need pip 21.3 or later. Hence the README now upgrades pip
  first.
- P-4. `license = {text = "MIT"}` in `pyproject.toml` triggered a setuptools
  deprecation that becomes a build error after 2027-02-18. The line was
  removed, and `License-File` and the classifier remain.
- P-5. The run-final example in the README showed a word-list entry instead
  of the run-final rule, so it was replaced with 呢張床好平，好麻煩呢？
- P-6. `set_jyutping` on a character missing from the data did nothing,
  while TeX reads such a character without context and with type `u`. Such
  a character is now its own run of type `u`, and the test
  `test_set_jyutping_char_not_in_data` covers this.
- P-7. `set_jyutping` rejected whitespace that `\setjyutping` ignores. It
  now strips spaces, tabs, CR and line feeds (LF), and the test
  `test_set_jyutping_ignores_spaces` covers this.

On the development Mac (Python 3.9), `Jyutping()` takes about 0.08 s and
`annotate` on 10 000 characters takes about 0.02 s.

## 2. How the port maps to the LaTeX package

| TeX (`xjyutping.sty`) | Python (`src/xjyutping/__init__.py`) |
| --- | --- |
| a character is Chinese iff `\xjp@c@<char>` exists | `c in self._chars` |
| runs: spaces and single line breaks between characters continue a run; `\par`/blank line ends it | `_runs` (ASCII space, tab, CR, LF; two line ends end the run; U+3000 ends it) |
| `\__xjyutping_flush:` (DP, 100000 per segment + 1 per single in `\xjp@cost@`, then the sum of `\xjp@k@` costs in `\xjp@lm@` since 1.5.0, `<=` so a full tie goes to the longer final word; bound `\xjp@e@` raw or canonical) | `_segment_run` (the same two values as a tuple; costs from `words.tsv` and `chars.tsv`; bound `_longest`, computed from `words.tsv` at load) |
| `\__xjyutping_emit:nn` word: raw key, else canonical; type `u` if `\xjp@uw@` | same, `self._user_words` |
| `\__xjyutping_lookup:nn` single: user, then `\xjp@f@` at run end, then default; type m/s from `\xjp@m@`; then `\__xjyutping_next:n` overrides a non-user reading from `\xjp@x@` (since 1.5.0) | same (`_user_chars`, `_next`, `_finals`, polyphone flag in `chars.tsv`) |
| `\__xjyutping_set:nnn` / `\__xjyutping_set_word:nn` | `set_jyutping` (raw and canonical keys, longest bound) |
| `debug` log `銀ngan4:w…` | `segment()` |

Beyond this mapping, the port differs from the TeX package by design in the
following ways.

- Since Python has no markup, the port has nothing like the command table,
  footnote runs, `\xjyutping` manual readings or plain mode. Therefore the
  parity corpus has TeX's commands resolved into the runs that TeX makes of
  them.
- `chars.tsv` lists the other readings of every character, not only of
  flagged polyphones, for use by `get_jyutpings`.
- `Segment` has no field for the other readings. The parity test reads them
  from `_chars`, while users get them through `get_jyutpings`.
- `get_jyutping` drops whitespace between Chinese characters, including
  U+3000, although U+3000 ends a run for segmentation.

## 3. Version 1.1.0

This version changed only the data and the documentation.

- The build of xjyutping-tex 1.2.0 copied its data into this package, with
  640 more characters, 2 291 more words and the two hand fixes.
- The parity file was regenerated with both TeX engines, and the two agree.
- `test_added_vocabulary` was added, and the README examples still run
  unchanged (24 doctests). Since `python -m doctest README.md` counts the
  closing code fence as expected output, strip the fences first and run the
  doctests with,

  ```bash
  PYTHONPATH=src python3 -c "import doctest,re; t=re.sub(r'(?m)^\x60{3}.*$','',open('README.md',encoding='utf8').read()); r=doctest.DocTestRunner(optionflags=doctest.NORMALIZE_WHITESPACE); r.run(doctest.DocTestParser().get_doctest(t,{},'README','README.md',0)); print(r.summarize())"
  ```
- The code did not change.
- To release to PyPI, run the commands below (the name `xjyutping` was free
  on 2026-09-28),

  ```bash
  python3 -m pip install --upgrade build twine
  python3 -m build
  python3 -m twine check dist/*
  python3 -m twine upload dist/*
  ```

  We built the 1.1.0 wheel and sdist this way and checked them.
  `twine check` passes, the wheel installs into a clean virtual environment
  and the 39 tests pass from the extracted sdist. `twine upload` asks for a
  PyPI API token, with the user name `__token__`. If in doubt, upload to
  TestPyPI first with `--repository testpypi`.

## 4. Version 1.2.0

This version changed the data, one test and the documentation, while the
code did not change.

- The build of xjyutping-tex 1.4.0 copied its data into this package.
  Specifically, ToJyutping chooses between the readings that rime gives a
  word (463 words) and adds 494 words, four particles have new defaults, and
  揾, 都會 and 係呢 are fixed. The LaTeX package's changelog, Part II,
  Section 9, describes how these choices were made and tested.
- The parity file was regenerated with both TeX engines, which agree.
- `test_tojyutping_readings` was added, so the suite now has 40 tests, and
  the 24 README examples still run unchanged.
- Measured against the 161 045 characters of HKCanCor, this package now reads
  94.08% of the characters correctly, against 92.09% for 1.1.0 and 92.78%
  for ToJyutping 3.2.0. The package gives the same readings as the LaTeX
  package, so the measurement applies to both.

## 5. Version 1.3.0

This version changed the segmentation for the first time since 1.0.0, so
both the data and the code changed.

- `_segment_run` keeps two values per position, the count of 100 000 per
  segment plus 1 per single character as before, and the sum of the costs
  of its words and single characters, and compares the two in order (`<=`
  on tuples, so that a full tie still goes to the longer final word). This
  matches `\xjp@cost@<i>` and `\xjp@lm@<i>` in `xjyutping.sty`. The cost of
  a word comes from the third column of `words.tsv`, that of a character from
  the fifth column of `chars.tsv`, and data without these columns gives cost
  0, which reproduces the old behaviour.
- A single character then looks up `next.tsv` with the three and then the two
  characters starting at it, by spelling and then by canonical spelling,
  before `finals.tsv` and its default. A character set with `set_jyutping`
  skips this, as in the LaTeX package.
- `set_jyutping` gives a word cost 0.
- The LaTeX package's changelog, Part II, Section 10, describes how the data
  was tuned and measured, and `jyutData/eval` of the workspace holds the
  scripts. The parity test was regenerated and the LaTeX package was checked
  against this package on 405 561 segments (704 484 characters) of all the
  corpora.

## 6. Open issues

- Readings that need more context than a word list gives, such as
  為 wai4/wai6, 當 dong1/dong3 and the tone of a particle in a question,
  stay wrong until a user sets them. The LaTeX package's changelog, Part II,
  Section 10.8, lists what remains after its 1.5.0.
- The licence of the book characters is still an open question, since the
  640 characters from 粵音資料集叢 come from data published without a
  licence statement (see `LICENSE` and the LaTeX package's changelog,
  Section 7.4).
