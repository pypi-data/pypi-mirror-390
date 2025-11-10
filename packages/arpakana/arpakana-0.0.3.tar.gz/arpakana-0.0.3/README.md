# arpakana

ARPAbet音素記号を日本語のカナ文字へ変換するためのシンプルなPythonライブラリです。

## 📖 概要

`arpakana` は、Carnegie Mellon University Pronouncing Dictionary形式のARPAbetを入力として、対応するカタカナ列を出力します。現在はコアとなる `arpabet_to_kana` 関数と、同機能をラップしたシンプルなCLIスクリプトを提供しています。

### 主な機能

- ARPAbetトークン列をカタカナへ変換する `arpabet_to_kana` 関数
- 末尾ストレス番号の正規化や子音クラスタの簡易処理
- `scripts/arpabet2kana.py` によるCLIユーティリティ

## � セットアップ

このリポジトリはまだPyPIに公開していません。ローカルで利用する場合は以下の手順でセットアップしてください。

```bash
git clone https://github.com/jiroshimaya/arpakana.git
cd arpakana
uv sync --all-extras
```

セットアップ後は `uv run` で各種コマンドを実行します。

## 💡 使用例

### Python API

```python
from arpakana.arpabet import arpabet_to_kana

greeting = arpabet_to_kana("HH AH0 L OW1")
assert greeting == "ハロウ"

words = ["B", "L", "UW"]
assert arpabet_to_kana(words) == "ブルー"

fallback = arpabet_to_kana("XYZ", unknown="*")
assert fallback == "*"
```

### CLI

```bash
uv run python scripts/arpabet2kana.py HH AH0 L OW1
# => ハロウ

echo "S K AY" | uv run python scripts/arpabet2kana.py
# => スカイ
```

## 🧪 テスト

```bash
uv run pytest
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細は [LICENSE](LICENSE) を参照してください。
