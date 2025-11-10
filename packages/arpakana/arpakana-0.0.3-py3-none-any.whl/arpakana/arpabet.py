"""ARPAbet phoneme helpers (optimized without sacrificing clarity)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# --------------------
# small fast helpers / precompiled stuff
# --------------------

_DIGITS = "0123456789"
_VOWELS = {"a", "i", "u", "e", "o"}
_KANA_RE = re.compile(r"^[\u30A0-\u30FFー]+$")


def _normalize_phoneme(token: str) -> str:
    """ARPAbet音素トークンを正規化する。

    Args:
        token: ARPAbet音素トークン（例: "AH0", "eh1"）

    Returns:
        正規化された音素（大文字、ストレス数字除去後）

    Examples:
        >>> _normalize_phoneme("AH0")
        'AH'
        >>> _normalize_phoneme("eh1")
        'EH'
        >>> _normalize_phoneme("  K2  ")
        'K'
    """
    return token.strip().upper().rstrip(_DIGITS)


_VOWEL_MAP: dict[str, tuple[str, ...]] = {
    "AA": ("a",),
    "AE": ("a",),
    "AH": ("a",),
    "AO": ("o",),
    "AW": ("a", "ウ"),
    "AX": ("a",),
    "AXR": ("a", "ー"),  # 互換性維持（事前に "AX R" へ展開する想定）
    "AY": ("a", "イ"),
    "EH": ("e",),
    "ER": ("a", "ー"),  # 互換性維持（事前に "AX R" へ展開する想定）
    "EY": ("e", "イ"),
    "IH": ("i",),
    "IX": ("i",),
    "IY": ("i", "ー"),
    "OW": ("o", "ウ"),
    "OY": ("o", "イ"),
    "OH": ("o", "ー"),
    "UH": ("u",),
    "UW": ("u", "ー"),
    "UX": ("u",),
}

_CV_TABLE: dict[tuple[str, ...], dict[str, str]] = {
    # Single consonants
    (): {"a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ"},
    ("B",): {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ"},
    ("CH",): {"a": "チャ", "i": "チ", "u": "チュ", "e": "チェ", "o": "チョ"},
    ("D",): {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    ("DH",): {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    ("DX",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("F",): {"a": "ファ", "i": "フィ", "u": "フ", "e": "フェ", "o": "フォ"},
    ("G",): {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ"},
    ("HH",): {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ"},
    ("JH",): {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("K",): {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ"},
    ("L",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("M",): {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ"},
    ("N",): {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    ("NG",): {"a": "ンガ", "i": "ンギ", "u": "ング", "e": "ンゲ", "o": "ンゴ"},
    ("NX",): {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    ("P",): {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ"},
    ("R",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("S",): {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    ("SH",): {"a": "シャ", "i": "シ", "u": "シュ", "e": "シェ", "o": "ショ"},
    ("T",): {"a": "タ", "i": "ティ", "u": "トゥ", "e": "テ", "o": "ト"},
    ("TH",): {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    ("V",): {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ"},
    ("W",): {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ウォ"},
    ("Y",): {"a": "ヤ", "i": "イ", "u": "ユ", "e": "イェ", "o": "ヨ"},
    ("Z",): {"a": "ザ", "i": "ズィ", "u": "ズ", "e": "ゼ", "o": "ゾ"},
    ("ZH",): {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    # Combined consonants
    ("K", "Y"): {"a": "キャ", "i": "キィ", "u": "キュ", "e": "キェ", "o": "キョ"},
    ("G", "Y"): {"a": "ギャ", "i": "ギィ", "u": "ギュ", "e": "ギェ", "o": "ギョ"},
    ("S", "Y"): {"a": "シャ", "i": "シィ", "u": "シュ", "e": "シェ", "o": "ショ"},
    ("Z", "Y"): {"a": "ジャ", "i": "ジィ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("T", "Y"): {"a": "チャ", "i": "チィ", "u": "チュ", "e": "チェ", "o": "チョ"},
    ("D", "Y"): {"a": "ジャ", "i": "ジィ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("H", "Y"): {"a": "ヒャ", "i": "ヒィ", "u": "ヒュ", "e": "ヒェ", "o": "ヒョ"},
    ("B", "Y"): {"a": "ビャ", "i": "ビィ", "u": "ビュ", "e": "ビェ", "o": "ビョ"},
    ("P", "Y"): {"a": "ピャ", "i": "ピィ", "u": "ピュ", "e": "ピェ", "o": "ピョ"},
    ("M", "Y"): {"a": "ミャ", "i": "ミィ", "u": "ミュ", "e": "ミェ", "o": "ミョ"},
    ("R", "Y"): {"a": "リャ", "i": "リィ", "u": "リュ", "e": "リェ", "o": "リョ"},
    ("L", "Y"): {"a": "リャ", "i": "リィ", "u": "リュ", "e": "リェ", "o": "リョ"},
    ("N", "Y"): {"a": "ニャ", "i": "ニィ", "u": "ニュ", "e": "ニェ", "o": "ニョ"},
    ("F", "Y"): {"a": "フャ", "i": "フィ", "u": "フュ", "e": "フェ", "o": "フョ"},
    ("T", "S"): {"a": "ツァ", "i": "ツィ", "u": "ツ", "e": "ツェ", "o": "ツォ"},
}

_STANDALONE_CONSONANTS: dict[tuple[str, ...], tuple[str, ...]] = {
    ("B",): ("ブ",),
    ("CH",): ("チ",),
    ("D",): ("ド",),
    ("DH",): ("ズ",),
    ("DX",): ("ル",),
    ("F",): ("フ",),
    ("G",): ("グ",),
    ("JH",): ("ジ",),
    ("K",): ("ク",),
    ("L",): ("ル",),
    ("M",): ("ン",),
    ("N",): ("ン",),
    ("NG",): ("ン",),
    ("NX",): ("ン",),
    ("P",): ("プ",),
    ("R",): ("ア",),
    ("S",): ("ス",),
    ("SH",): ("シュ",),
    ("T",): ("トゥ",),
    ("TH",): ("ス",),
    ("V",): ("ヴ",),
    ("Z",): ("ズ",),
    ("ZH",): ("ジュ",),
    ("T", "S"): ("ツ",),
}

_SOKUON_CLUSTERS: set[tuple[str, ...]] = {
    ("CH",),
    ("SH",),
    ("JH",),
    ("ZH",),
    ("T", "S"),
}

_SILENCES = {"", "SIL", "SP", "SPN"}

_KNOWN_PHONEMES: set[str] = (
    set(_VOWEL_MAP)
    | {symbol for key in _CV_TABLE for symbol in key}
    | {symbol for cluster in _STANDALONE_CONSONANTS for symbol in cluster}
    | _SILENCES
)

# --------------------
# precomputed maps for fast sequence replacement
# --------------------

# 子音群 + 母音 → カナ の完全展開（最長一致のため長さ別も保持）
_CV_SEQ2KANA: dict[tuple[str, ...], str] = {}
for cons, table in _CV_TABLE.items():
    for vcore, kana in table.items():
        _CV_SEQ2KANA[(*cons, vcore)] = kana
_R_SEQ2KANA: dict[tuple[str, ...], str] = {
    k: v for k, v in _CV_SEQ2KANA.items() if k and k[0] == "R"
}  # R単独用

# 照合に使う長さ一覧を降順で（最長一致）
_CV_LENGTHS_DESC = sorted({len(k) for k in _CV_SEQ2KANA}, reverse=True)
_R_LENGTHS_DESC = sorted({len(k) for k in _R_SEQ2KANA}, reverse=True)
_STANDALONE_LENGTHS_DESC = sorted(
    {len(k) for k in _STANDALONE_CONSONANTS}, reverse=True
)


def _expand_vowel_with_r(phoneme: list[str]) -> list[str]:
    """R音を含む母音を展開する。

    Args:
        phoneme: 音素のリスト

    Returns:
        ER/AXRが AX R に展開された音素リスト

    Examples:
        >>> _expand_vowel_with_r(["B", "ER", "D"])
        ['B', 'AX', 'R', 'D']
        >>> _expand_vowel_with_r(["AXR", "T"])
        ['AX', 'R', 'T']

    Note:
        互換性維持のため、ERとAXRの両方をサポート。
        通常はER → AX R に変換される。
    """
    replaced: list[str] = []
    for p in phoneme:
        if p in ("ER", "AXR"):
            replaced.extend(("AX", "R"))
        else:
            replaced.append(p)
    return replaced


def _normalize_vowel(phoneme: list[str]) -> list[str]:
    """母音音素を日本語音韻に正規化する。

    Args:
        phoneme: 音素のリスト

    Returns:
        母音が日本語の基本母音（a, i, u, e, o）や特殊音（ー、ウ、イ）に
        正規化された音素リスト

    Examples:
        >>> _normalize_vowel(["AA", "K"])
        ['a', 'K']
        >>> _normalize_vowel(["AY", "T"])
        ['a', 'イ', 'T']
        >>> _normalize_vowel(["OW"])
        ['o', 'ウ']

    Note:
        _VOWEL_MAPを使用してARPAbet母音を日本語音韻にマッピング。
        二重母音（AY, OW等）は複数の音素に展開される。
    """
    out: list[str] = []
    for p in phoneme:
        if p in _VOWEL_MAP:
            out.extend(_VOWEL_MAP[p])  # tupleのままでOK
        else:
            out.append(p)
    return out


def _insert_sokuon(phoneme: list[str]) -> list[str]:
    """母音の後に特定の子音群が続く場合に促音「ッ」を挿入する。

    Args:
        phoneme: 音素のリスト

    Returns:
        適切な位置に促音が挿入された音素リスト

    Examples:
        >>> _insert_sokuon(["a", "CH", "i"])
        ['a', 'ッ', 'CH', 'i']
        >>> _insert_sokuon(["K", "a", "SH"])
        ['K', 'a', 'ッ', 'SH']
        >>> _insert_sokuon(["a", "K", "i"])  # Kは促音対象外
        ['a', 'K', 'i']

    Note:
        _SOKUON_CLUSTERS（CH, SH, JH, ZH, TS）に該当する子音群の前で、
        直前が母音の場合のみ促音を挿入する。最長一致で判定。
    """
    if not phoneme:
        return []
    result = [phoneme[0]]
    # 最長一致のため長さ降順
    cluster_lengths = sorted({len(c) for c in _SOKUON_CLUSTERS}, reverse=True)

    i = 1
    n = len(phoneme)
    while i < n:
        for L in cluster_lengths:
            if (
                i + L <= n
                and tuple(phoneme[i : i + L]) in _SOKUON_CLUSTERS
                and result[-1] in _VOWELS
            ):
                result.append("ッ")
                break
        result.append(phoneme[i])
        i += 1
    return result


def _apply_cv_r_rules(tokens: list[str]) -> list[str]:
    """子音+母音+Rの組み合わせをカナに変換する。

    Args:
        tokens: 音素トークンのリスト

    Returns:
        R音を含む子音+母音の組み合わせが変換された音素リスト

    Examples:
        >>> _apply_cv_r_rules(["R", "a"])
        ['ラ']
        >>> _apply_cv_r_rules(["B", "R", "a"])
        ['B', 'ラ']

    Note:
        _R_SEQ2KANAマップを使用して最長一致で変換。
        Rで始まる音素列を優先的に処理する。
    """
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _R_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i : i + L])
                kana = _R_SEQ2KANA.get(key)
                if kana is not None:
                    out.append(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out


def _apply_standalone_r_rules(tokens: list[str]) -> list[str]:
    """単独のR音を文脈に応じて変換する。

    Args:
        tokens: 音素トークンのリスト

    Returns:
        単独R音が適切に変換された音素リスト

    Examples:
        >>> _apply_standalone_r_rules(["R", "i"])
        ['ア', 'i']
        >>> _apply_standalone_r_rules(["a", "R"])
        ['a', 'ー']
        >>> _apply_standalone_r_rules(["i", "R"])
        ['i', 'ア']
        >>> _apply_standalone_r_rules(["o", "R", "a"])
        ['o', 'ー', 'a']

    Note:
        - 語頭のR → ア
        - a,oの後のR → ー（長音）
        - 連続する長音の後のR → 無視
        - その他のR → ア
    """
    if not tokens:
        return []
    out: list[str] = []
    out.append("ア" if tokens[0] == "R" else tokens[0])
    for i, phoneme in enumerate(tokens[1:], start=1):
        if phoneme == "R":
            if tokens[i - 1] in {"a", "o"}:
                out.append("ー")
            elif tokens[i - 1] == "ー":
                pass
            else:
                out.append("ア")
        else:
            out.append(phoneme)
    return out


def _apply_r_rules(tokens: list[str]) -> list[str]:
    """R音変換規則を統合的に適用する。

    Args:
        tokens: 音素トークンのリスト

    Returns:
        R音変換規則が適用された音素リスト

    Note:
        CV+R規則を先に適用し、その後単独R規則を適用する。
        この順序により、適切なR音変換を実現する。
    """
    after_cv = _apply_cv_r_rules(tokens)
    after_standalone = _apply_standalone_r_rules(after_cv)
    return after_standalone


def _apply_cv_rules(tokens: list[str]) -> list[str]:
    """子音+母音の組み合わせをカナに変換する。

    Args:
        tokens: 音素トークンのリスト

    Returns:
        子音+母音の組み合わせがカナに変換された音素リスト

    Examples:
        >>> _apply_cv_rules(["K", "a", "T"])
        ['カ', 'T']
        >>> _apply_cv_rules(["SH", "i"])
        ['シ']
        >>> _apply_cv_rules(["T", "Y", "o"])
        ['チョ']

    Note:
        _CV_SEQ2KANAマップを使用して最長一致で変換。
        複合子音（KY, SH等）も適切に処理される。
    """
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _CV_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i : i + L])
                kana = _CV_SEQ2KANA.get(key)
                if kana is not None:
                    out.append(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out


def _apply_standalone_consonant_rules(tokens: list[str]) -> list[str]:
    """単独子音をカナに変換する。

    Args:
        tokens: 音素トークンのリスト

    Returns:
        単独子音がカナに変換された音素リスト

    Examples:
        >>> _apply_standalone_consonant_rules(["K"])
        ['ク']
        >>> _apply_standalone_consonant_rules(["N", "G"])
        ['ン']
        >>> _apply_standalone_consonant_rules(["T", "S"])
        ['ツ']

    Note:
        _STANDALONE_CONSONANTSマップを使用して最長一致で変換。
        母音が続かない子音を適切なカナに変換する。
        一部の子音は複数のカナに展開される場合がある。
    """
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _STANDALONE_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i : i + L])
                kana = _STANDALONE_CONSONANTS.get(key)
                if kana is not None:
                    out.extend(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out


def _convert_unknown_token(phoneme: list[str], unknown: str) -> list[str]:
    """変換できない音素を指定文字に置換する。

    Args:
        phoneme: 音素のリスト
        unknown: 未知音素の置換文字

    Returns:
        カナ以外の音素が置換された音素リスト

    Examples:
        >>> _convert_unknown_token(["カ", "XX", "タ"], "?")
        ['カ', '?', 'タ']
        >>> _convert_unknown_token(["シ", "YY", "ZZ"], "〇")
        ['シ', '〇', '〇']

    Note:
        カタカナ文字以外の音素を指定された文字に置換する。
        _KANA_REで正規表現マッチングを行う。
    """
    return [p if _KANA_RE.match(p) else unknown for p in phoneme]


def arpabet_to_kana(phonemes: str | Iterable[str], *, unknown: str = "?") -> str:
    """ARPAbet音素列をカタカナに変換する。

    Args:
        phonemes: ARPAbet音素のリスト。文字列の場合はスペース区切り、
                 Iterableの場合は各要素が個別の音素トークン。
                 例: "HH EH1 L OW0" または ["HH", "EH1", "L", "OW0"]
        unknown: 変換できない音素を置き換える文字。デフォルトは "?"。

    Returns:
        変換されたカタカナ文字列。

    Examples:
        >>> arpabet_to_kana("HH EH1 L OW0")
        'ヘロウ'
        >>> arpabet_to_kana(["K", "AE1", "T"])
        'キャット'
        >>> arpabet_to_kana("XX YY ZZ", unknown="〇")
        '〇〇〇'

    Note:
        変換処理は以下の順序で実行される：
        1. 音素の正規化（大文字化、ストレス記号除去）
        2. ER/AXRの展開（AX R に分解）
        3. 母音の正規化
        4. 促音の挿入
        5. R音素の変換規則適用
        6. 子音+母音の組み合わせ変換
        7. 単独子音の変換
        8. 未知音素の置換
    """
    tokens = phonemes.split() if isinstance(phonemes, str) else list(phonemes)
    normalized = [_normalize_phoneme(t) for t in tokens if t.strip()]

    expanded_r = _expand_vowel_with_r(normalized)
    normalized_vowels = _normalize_vowel(expanded_r)
    with_sokuon = _insert_sokuon(normalized_vowels)
    after_r = _apply_r_rules(with_sokuon)
    after_cv = _apply_cv_rules(after_r)
    after_standalone = _apply_standalone_consonant_rules(after_cv)
    with_unknowns = _convert_unknown_token(after_standalone, unknown)

    return "".join(with_unknowns)


__all__ = ["arpabet_to_kana"]
