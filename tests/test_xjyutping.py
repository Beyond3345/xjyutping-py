"""Tests for xjyutping, following xpinyin's tests where they make sense."""
import re
from pathlib import Path

import pytest

import xjyutping
from xjyutping import DATA_DIR, Jyutping, Segment

HERE = Path(__file__).resolve().parent


@pytest.fixture(scope='module')
def jyutping():
    return Jyutping()


def test_version():
    assert re.fullmatch(r'\d+\.\d+\.\d+', xjyutping.__version__)   # Semantic Versioning
    pyproject = HERE.parent / 'pyproject.toml'
    if pyproject.exists():      # a source checkout
        assert 'version = "%s"' % xjyutping.__version__ in pyproject.read_text(encoding='utf8')


def test_data_dir():
    assert Jyutping(str(DATA_DIR)).get_jyutping('香港') == 'hoeng1-gong2'


# --- get_jyutping ------------------------------------------------------------

def test_get_jyutping_with_default_splitter(jyutping):
    assert jyutping.get_jyutping('香港') == 'hoeng1-gong2'


def test_get_jyutping_with_splitter(jyutping):
    assert jyutping.get_jyutping('香港', splitter='') == 'hoeng1gong2'
    assert jyutping.get_jyutping('香港', ' ') == 'hoeng1 gong2'


def test_get_jyutping_mixed_words(jyutping):
    assert jyutping.get_jyutping('Apple發布iOS7', splitter='-') == 'Apple-faat3-bou3-iOS7'


def test_get_jyutping_spaces(jyutping):
    # spaces between Chinese characters are dropped, other text is kept
    assert jyutping.get_jyutping('你好 世界') == 'nei5-hou2-sai3-gaai3'
    assert jyutping.get_jyutping(' 香港 ') == ' -hoeng1-gong2- '


def test_get_jyutping_convert(jyutping):
    assert jyutping.get_jyutping('香港', convert='upper') == 'HOENG1-GONG2'
    assert jyutping.get_jyutping('香港', convert='capitalize') == 'Hoeng1-Gong2'
    with pytest.raises(ValueError):
        jyutping.get_jyutping('香港', convert='title')


def test_tone_marks(jyutping):
    assert jyutping.get_jyutping('香港', tone_marks='numbers') == 'hoeng1-gong2'
    assert jyutping.get_jyutping('香港', tone_marks=None) == 'hoeng-gong'
    assert jyutping.get_jyutping('好行', ' ', tone_marks='fancy') == 'hou\u02ca\u00b2 haang\u02ce\u2084'
    assert jyutping.get_jyutping('好行', ' ', tone_marks='discord') == 'hou\u2e0d\u00b2 haang\u2e1c\u2084'
    with pytest.raises(ValueError):
        jyutping.get_jyutping('香港', tone_marks='marks')
    with pytest.raises(ValueError):
        jyutping.get_jyutping('', tone_marks='marks')


@pytest.mark.parametrize('style, marks', [
    ('fancy', ['\u02c9\u00b9', '\u02ca\u00b2', '\u02d7\u2083', '\u02ce\u2084', '\u02cf\u2085', '\u02cd\u2086']),
    ('discord', ['\u02c9\u00b9', '\u2e0d\u00b2', '-\u2083', '\u2e1c\u2084', '\u2e1d\u2085', '\u02cd\u2086']),
])
def test_decode_jyutping(style, marks):
    assert [Jyutping.decode_jyutping('si%d' % t, style) for t in range(1, 7)] == ['si' + m for m in marks]
    assert Jyutping.decode_jyutping('si', style) == 'si'    # no tone: unchanged
    assert Jyutping.decode_jyutping('si3', None) == 'si'


def test_convert_jyutping():
    assert Jyutping.convert_jyutping('hoeng1', 'upper') == 'HOENG1'
    assert Jyutping.convert_jyutping('HOENG1', 'lower') == 'hoeng1'


# --- context -------------------------------------------------------------

def test_context(jyutping):
    assert jyutping.get_jyutping('銀行') == 'ngan4-hong4'
    assert jyutping.get_jyutping('行路') == 'haang4-lou6'
    assert jyutping.get_jyutping('校長') == 'haau6-zoeng2'
    assert jyutping.get_jyutping('長期') == 'coeng4-kei4'
    assert jyutping.get_jyutping('還有') == 'waan4-jau5'
    assert jyutping.get_jyutping('瞓覺') == 'fan3-gaau3'
    assert jyutping.get_jyutping('中咗') == 'zung3-zo2'


def test_segmentation(jyutping):
    # fewest words, then fewest single characters
    assert [s.text for s in jyutping.segment('學校長大')] == ['學校', '長大']
    assert jyutping.segment('我哋去銀行，佢重未嚟') == [
        Segment('我哋', ['ngo5', 'dei6'], 'w'), Segment('去', ['heoi3'], 's'),
        Segment('銀行', ['ngan4', 'hong4'], 'w'), Segment('佢', ['keoi5'], 's'),
        Segment('重', ['zung6'], 'm'), Segment('未', ['mei6'], 's'),
        Segment('嚟', ['lai4'], 'm')]


def test_run_final_reading(jyutping):
    assert jyutping.annotate('呢張床')[0] == ('呢', 'ni1')
    assert jyutping.annotate('好麻煩呢？')[3] == ('呢', 'ne1')
    assert jyutping.annotate('呢')[0] == ('呢', 'ne1')


def test_added_vocabulary(jyutping):
    # words from CC-Canto and the CC-CEDICT Cantonese readings (1.1.0)
    assert jyutping.get_jyutping('機長廣播', ' ') == 'gei1 zoeng2 gwong2 bo3'
    assert jyutping.get_jyutping('營業額', ' ') == 'jing4 jip6 ngaak2'
    assert jyutping.get_jyutping('自由行旅客', ' ') == 'zi6 jau4 hang4 leoi5 haak3'
    # ... but not where they would take a character from its neighbour
    assert jyutping.get_jyutping('這個方法會否', ' ').endswith('faat3 wui5 fau2')
    assert jyutping.get_jyutping('碳水化合物', ' ') == 'taan3 seoi2 faa3 hap6 mat6'
    # characters that only the books of cantonese-books-data have
    assert jyutping.annotate('鿃') == [('鿃', 'sim2')]


def test_tojyutping_readings(jyutping):
    # 1.2.0: ToJyutping picks between the readings rime gives a word
    assert jyutping.get_jyutping('公園價錢', ' ') == 'gung1 jyun2 gaa3 cin4'
    assert jyutping.get_jyutping('澳門郵局', ' ') == 'ou3 mun2 jau4 guk2'
    # the modal 會 after 都, while 'metropolis' keeps wui6
    assert jyutping.get_jyutping('我哋都會去', ' ') == 'ngo5 dei6 dou1 wui5 heoi3'
    assert jyutping.get_jyutping('國際大都會', ' ') == 'gwok3 zai3 daai6 dou1 wui6'
    # 揾 is 搵, 呢 before 就 is the particle, and the particle defaults
    assert jyutping.get_jyutping('去揾佢', ' ') == 'heoi3 wan2 keoi5'
    assert jyutping.get_jyutping('佢呢就走', ' ') == 'keoi5 ne1 zau6 zau2'
    assert jyutping.get_jyutping('但係呢', ' ') == 'daan6 hai6 ne1'
    assert jyutping.get_jyutping('好正囖', ' ') == 'hou2 zeng3 lo1'
    assert jyutping.get_jyutping('係㗎得嘞', ' ') == 'hai6 gaa3 dak1 laak3'


def test_corpus_tuned_readings(jyutping):
    # 1.3.0: 呢 alone is the particle, and the demonstrative before a
    # classifier or a number, unless a word such as 一定 follows
    assert jyutping.get_jyutping('呢間酒店', ' ') == 'ni1 gaan1 zau2 dim3'
    assert jyutping.get_jyutping('佢呢一定唔肯', ' ') == 'keoi5 ne1 jat1 ding6 m4 hang2'
    assert jyutping.get_jyutping('啲錢呢邊個畀你', ' ').split()[2] == 'ne1'
    # 重 alone is 'still', 'heavy' comes from words; 咁 'like this' is gam2
    assert jyutping.get_jyutping('佢重有一個', ' ').split()[1] == 'zung6'
    assert jyutping.get_jyutping('好重', ' ') == 'hou2 cung5'
    assert jyutping.get_jyutping('就係咁', ' ') == 'zau6 hai6 gam2'
    assert jyutping.get_jyutping('咁樣做', ' ') == 'gam2 joeng2 zou6'
    assert jyutping.get_jyutping('咁大', ' ') == 'gam3 daai6'
    # particles: the usual tone at the end of a word, standard spellings
    assert jyutping.get_jyutping('你做乜啊', ' ') == 'nei5 zou6 mat1 aa3'
    assert jyutping.get_jyutping('下星期啦', ' ') == 'haa6 sing1 kei4 laa1'
    assert jyutping.get_jyutping('嗯') == 'm6'
    assert not [w for w, r in jyutping._words.items()
                if re.search(r'\b(la[134]|a[13]|ga[34]|ma3|za3)\b', r)]


def test_frequency_tie_break(jyutping):
    # among splits with as many words and single characters, the most usual
    # words win, not the longer final word
    assert [s.text for s in jyutping.segment('步行街')] == ['步行', '街']
    assert jyutping.get_jyutping('之後改名叫北京', ' ') == 'zi1 hau6 goi2 meng2 giu3 bak1 ging1'
    assert jyutping.get_jyutping('影相等活動', ' ') == 'jing2 soeng2 dang2 wut6 dung6'
    assert jyutping.get_jyutping('有人為咗照顧佢', ' ').split()[2] == 'wai6'
    # a word set by the user wins such a tie
    j = Jyutping()
    j.set_jyutping('行街', 'haang4 gaai1')
    assert [s.text for s in j.segment('步行街')] == ['步', '行街']


def test_variants(jyutping):
    assert jyutping.get_jyutping('因為') == jyutping.get_jyutping('因爲') == 'jan1-wai6'
    assert jyutping.get_jyutping('裡面') == jyutping.get_jyutping('裏面') == 'leoi5-min6'
    assert jyutping.get_jyutping('説話') == jyutping.get_jyutping('說話') == 'syut3-waa6'


def test_runs(jyutping):
    assert jyutping.get_jyutping('銀\n行') == 'ngan4-hong4'      # a line break keeps the run
    assert jyutping.get_jyutping('銀\n\n行') == 'ngan4-haang4'   # a blank line ends it
    assert jyutping.get_jyutping('銀，行') == 'ngan4-，-haang4'


def test_runs_cr_line_ends(jyutping):
    # TeX ends a line at LF, CR or CRLF (frozen from the TeX package's log)
    assert jyutping.get_jyutping('佢好辛苦呢\r\r銀\r\r行') == 'keoi5-hou2-san1-fu2-ne1-ngan4-haang4'
    assert [s.text for s in jyutping.segment('行\r\n乙\n\r丙')] == ['行', '乙', '丙']
    assert jyutping.get_jyutping('銀\r\n行') == 'ngan4-hong4'
    assert jyutping.get_jyutping('銀\r\n\r行') == 'ngan4-haang4'


# --- set_jyutping ----------------------------------------------------------

def test_set_jyutping_char():
    j = Jyutping()
    j.set_jyutping('重', 'zung6')
    assert j.segment('佢重未嚟')[1] == Segment('重', ['zung6'], 'u')
    assert j.get_jyutping('重新') == 'cung4-san1'   # words still win


def test_set_jyutping_word():
    j = Jyutping()
    j.set_jyutping('重話', 'zung6 waa6')
    assert j.segment('句重話')[-1] == Segment('重話', ['zung6', 'waa6'], 'u')
    j.set_jyutping('銀行', ' ngan4  hong2 ')      # beats the word list
    assert j.segment('銀行') == [Segment('銀行', ['ngan4', 'hong2'], 'u')]
    j.set_jyutping('一二三四五六七八九', 'jat1 ji6 saam1 sei3 ng5 luk6 cat1 baat3 gau2')
    assert len(j.segment('一二三四五六七八九')) == 1


def test_set_jyutping_variant_spelling():
    j = Jyutping()
    j.set_jyutping('為食', 'wai6 sik6')
    assert j.segment('爲食') == [Segment('爲食', ['wai6', 'sik6'], 'u')]


def test_set_jyutping_char_not_in_data():
    # like \setjyutping: read without context, and it ends the run (TeX log)
    j = Jyutping()
    j.set_jyutping('\U0002a736', 'keoi5')
    assert j.segment('\U0002a736哋去咗') == [
        Segment('\U0002a736', ['keoi5'], 'u'), Segment('哋', ['dei6'], 's'),
        Segment('去', ['heoi3'], 's'), Segment('咗', ['zo2'], 's')]
    assert j.annotate('\U0002a736哋')[0] == ('\U0002a736', 'keoi5')
    assert j.get_jyutpings('\U0002a736哋')[0] == 'keoi5-dei6'


def test_set_jyutping_ignores_spaces():
    j = Jyutping()
    j.set_jyutping('重 話', 'zung6 waa6')
    assert j.segment('佢重話唔去')[1] == Segment('重話', ['zung6', 'waa6'], 'u')


def test_set_jyutping_count_mismatch():
    j = Jyutping()
    with pytest.raises(ValueError):
        j.set_jyutping('銀行', 'ngan4')
    with pytest.raises(ValueError):
        j.set_jyutping('', '')
    with pytest.raises(ValueError):
        j.set_jyutping(' ', 'si1')


# --- annotate ----------------------------------------------------------------

def test_annotate(jyutping):
    assert jyutping.annotate('我哋 go 銀行！') == [
        ('我', 'ngo5'), ('哋', 'dei6'), (' ', None), ('g', None), ('o', None),
        (' ', None), ('銀', 'ngan4'), ('行', 'hong4'), ('！', None)]
    assert jyutping.annotate('行', tone_marks='fancy') == [('行', 'haang\u02ce\u2084')]


# --- initials ------------------------------------------------------------

def test_get_initial(jyutping):
    assert jyutping.get_initial('你') == 'N'
    assert jyutping.get_initial('A') == 'A'


def test_get_initials(jyutping):
    assert jyutping.get_initials('你好') == 'N-H'
    assert jyutping.get_initials('銀行') == 'N-H'


def test_get_initials_with_splitter(jyutping):
    assert jyutping.get_initials('你好', ' ') == 'N H'
    assert jyutping.get_initials('你好', '') == 'NH'


def test_get_initials_full(jyutping):
    assert jyutping.get_initials('我去廣州', full=True) == 'NG-H-GW-Z'
    assert jyutping.get_initials('群', full=True) == 'KW'
    # no initial consonant: 唔 m4, 五 ng5 (syllabic nasals), 屋 uk1
    assert jyutping.get_initials('唔五屋', full=True) == '--'
    assert jyutping.get_initials('唔五屋') == 'M-N-U'


# --- combinations ------------------------------------------------------------

def test_get_jyutpings_with_default_splitter(jyutping):
    assert jyutping.get_jyutpings('香港') == ['hoeng1-gong2']


def test_get_jyutpings_single_char(jyutping):
    assert jyutping.get_jyutpings('行', splitter='') == ['haang4', 'hang4', 'hong4', 'hong2', 'hang6']


def test_get_jyutpings_context_first(jyutping):
    combs = jyutping.get_jyutpings('銀行', n=100)
    assert combs[0] == 'ngan4-hong4'
    assert len(combs) == len(set(combs)) == 5


def test_get_jyutpings_two_chars(jyutping):
    combs1 = jyutping.get_jyutpings('音', splitter='', n=100)
    combs2 = jyutping.get_jyutpings('樂', splitter='', n=100)
    combs12 = jyutping.get_jyutpings('音樂', splitter='', n=100)
    assert len(combs12) == len(combs1) * len(combs2)
    assert combs12[0] == 'jam1ngok6'


def test_get_jyutpings_no_tones_uniq(jyutping):
    assert jyutping.get_jyutpings('行', tone_marks=None) == ['haang', 'hang', 'hong']


def test_get_jyutpings_max_num(jyutping):
    assert len(jyutping.get_jyutpings('音樂', splitter='', n=2)) == 2


def test_get_jyutpings_mixed_words(jyutping):
    assert jyutping.get_jyutpings('ABC長123', splitter=' ') == ['ABC coeng4 123', 'ABC zoeng2 123']


def test_get_jyutpings_long_seq(jyutping):
    text = (HERE / 'parity_corpus.txt').read_text(encoding='utf8')
    assert len(jyutping.get_jyutpings(text, n=20)) == 20
    assert len(jyutping.get_jyutpings(text)) == 10   # limited to 10 by default


def test_empty(jyutping):
    assert jyutping.get_jyutping('') == ''
    assert jyutping.get_jyutpings('') == ['']
    assert jyutping.annotate('') == []
    assert jyutping.segment('') == []
    assert jyutping.get_initials('') == ''


# --- parity with the TeX package -------------------------------------------

def test_parity_with_tex_package():
    """Every segment, reading and type equals the TeX package's debug log.

    parity_corpus.txt is plain text with \\setjyutping lines; it starts with
    the text of xjyutping-tex/tests/regression.tex, its commands resolved into
    the runs TeX makes of them.  parity_expected.txt is the debug log of
    parity.tex (see there), frozen from xjyutping-tex 1.2.0.
    """
    j = Jyutping()
    corpus = (HERE / 'parity_corpus.txt').read_text(encoding='utf8')
    parts = re.split(r'\\setjyutping\{(.*?)\}\{(.*?)\}', corpus)
    got = []
    for k in range(0, len(parts), 3):
        for s in j.segment(parts[k]):
            log = ''.join('%s%s:%s' % (c, r, s.type) for c, r in zip(s.text, s.readings))
            if s.type == 'm':
                log += '(%s)' % ' '.join(j._chars[s.text][1])
            got.append(log)
        if k + 2 < len(parts):
            j.set_jyutping(parts[k + 1], parts[k + 2])
    lines = (HERE / 'parity_expected.txt').read_text(encoding='utf8').splitlines()
    expected = [seg for line in lines for seg in line[len('xjyutping> '):-len(' |')].split(' |')]
    assert len(expected) > 400
    assert got == expected
