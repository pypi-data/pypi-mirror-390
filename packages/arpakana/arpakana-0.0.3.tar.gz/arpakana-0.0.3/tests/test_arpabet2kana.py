from arpakana.arpabet import arpabet_to_kana


def test_正常系_基本単語() -> None:
    # hello
    assert arpabet_to_kana("HH AH0 L OW1") == "ハロウ"
    # sky
    assert arpabet_to_kana("S K AY") == "スカイ"
    # blue
    assert arpabet_to_kana(["B", "L", "UW"]) == "ブルー"
    # train
    assert arpabet_to_kana("T R EY N") == "トゥレイン"
    # bout
    assert arpabet_to_kana("B AW1 T") == "バウトゥ"
    # 'cause
    assert arpabet_to_kana("K AH0 Z") == "カズ"
    # 'course
    assert arpabet_to_kana("K AO1 R S") == "コース"
    # 'm
    assert arpabet_to_kana("AH0 M") == "アン"
    # frisco
    assert arpabet_to_kana("F R IH1 S K OW0") == "フリスコウ"


def test_正常系_長い発音() -> None:
    arpabet_sequence = [
        "P",
        "OH",
        "K",
        "S",
        "DX",
        "T",
        "AO",
        "K",
        "IH",
        "JH",
        "EH",
        "L",
        "K",
        "IH",
        "JH",
        "IH",
        "K",
        "OH",
        "K",
        "UW",
        "R",
        "AE",
        "K",
        "UW",
        "DX",
        "EH",
        "K",
        "IH",
        "V",
        "AE",
        "N",
        "JH",
        "IH",
        "G",
        "AE",
        "T",
        "OH",
        "R",
        "AE",
        "K",
        "S",
        "AE",
        "N",
        "EH",
        "N",
        "AE",
    ]
    assert (
        arpabet_to_kana(arpabet_sequence)
        == "ポークスルトキッジェルキッジコークーラクーレキヴァンジガトーラクサネナ"
    )


def test_正常系_複合子音() -> None:
    # cues
    assert arpabet_to_kana("K Y UW1 Z") == "キューズ"
    # aquamarine
    assert arpabet_to_kana("AA K W AH M ER IY N") == "アクワマリーン"


def test_正常系_TS音素() -> None:
    # cats
    assert arpabet_to_kana("K AE1 T S") == "カッツ"
    # watches
    assert arpabet_to_kana("W AA1 CH IH0 Z") == "ワッチズ"
    # abducts
    assert arpabet_to_kana("AE0 B D AH1 K T S") == "アブダクツ"


def test_正常系_NG音素() -> None:
    # quote
    assert arpabet_to_kana("K W OW1 T") == "クウォウトゥ"
    # bengtson
    assert arpabet_to_kana("B EH1 NG T S AH0 N") == "ベンツァン"
    # fourthquarter
    assert arpabet_to_kana("F AO1 R TH K W AO1 R T ER0") == "フォースクウォーター"


def test_正常系_R() -> None:
    # amateurish
    assert arpabet_to_kana("AE1 M AH0 CH ER2 IH0 SH") == "アマッチャリッシュ"
    # ameliorate
    assert arpabet_to_kana("AH0 M IY1 L Y ER0 EY2 T") == "アミーリャレイトゥ"
    # bird
    assert arpabet_to_kana("B ER1 D") == "バード"
    # fear
    assert arpabet_to_kana("F IH1 R") == "フィア"
    # bear
    assert arpabet_to_kana("B EH1 R") == "ベア"
    # before
    assert arpabet_to_kana("B IH0 F AO1 R") == "ビフォー"
    # aboard
    assert arpabet_to_kana("AH0 B AO1 R D") == "アボード"
    # sure
    assert arpabet_to_kana("SH UH1 R") == "シュア"


def test_正常系_未知トークン() -> None:
    assert arpabet_to_kana("XYZ", unknown="*") == "*"


def test_促音挿入ルール() -> None:
    # rich
    assert arpabet_to_kana("R IH1 CH") == "リッチ"
    # beach
    assert arpabet_to_kana("B IY1 CH") == "ビーチ"
    # fish
    assert arpabet_to_kana("F IH1 SH") == "フィッシュ"
    # marsh
    assert arpabet_to_kana("M AA1 R SH") == "マーシュ"
    # boots
    assert arpabet_to_kana("B UW1 T S") == "ブーツ"
