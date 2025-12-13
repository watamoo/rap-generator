# 🎤 Rap Generator – 日本語ラップ韻検索 & 生成ツール

**Rap Generator**は、日本語ラップの韻を踏んだ歌詞を生成するためのツールです。  
[in-note.com](https://in-note.com) から取得した韻データをもとに、類似した発音を持つ語句を検索し、ラップの生成に活用できます。

---

## 🧱 セットアップ手順

### 環境準備

Python 3.12以上が必要です。  
[uv](https://github.com/astral-sh/uv) を使用して仮想環境・依存解決を高速に行います。

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 依存関係のインストール

```sh
uv sync
```
---

## ⚙️ 機能一覧

### rhyme_scraper.py
この処理は時間がかかるため、データの一部を抜粋したデータを `data/in_note_rhymes_compressed.csv` に格納しています。
まずはそちらのcsvを使って試してみてください。

[in-note.com](https://in-note.com) から韻のデータを収集し、以下のCSV形式で `data/in_note_rhymes.csv` に保存します。

- `target_word`: 対象単語
- `rhyme_word`: 韻を踏む単語
- `reading`: ひらがな読み
- `n_chars`: 文字数

### rhyme_mcp_server.py

mcpを用いた韻検索APIサーバです。  
以下の2つのコマンドを提供します。

- `get_rhymes`: 指定した単語に対する韻を検索
- `get_available_words`: 利用可能な単語一覧を取得

---

## 🖥️ ローカルでのMCPサーバ構築手順

1. 任意のローカルフォルダを作成し、その中に以下を配置します:
   - `rhyme_mcp_server.py`
   - `data/in_note_rhymes.csv`

2. ClineまたはClaude AppなどのMCP対応ツールの設定ファイルに以下を追加します：

```json
{
  "mcpServers": {
    "rhyme_search": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/your/folder",
        "run",
        "rhyme_mcp_server.py"
      ],
      "alwaysAllow": [
        "get_available_words",
        "get_rhymes"
      ]
    }
  }
}
```

---

## 🧠 Clineでのカスタムプロンプト設定

1. Clineでモード編集画面を開きます
2. 任意のモード名を設定し、`prompt/custom_prompt.txt`の内容を**モード固有のカスタム指示**として入力します：

---

## 🎧 曲化の手順（Suno活用）

1. [Suno](https://suno.com) を開く
2. `Lyrics` にラップ歌詞を入力
3. `Styles` に次の文字列を入力：

```
hip-hop rap battle, very fast tempo, rhythmically tight
```

4. `Create` をクリックして曲を生成

### ✍️ Suno用の歌詞記述のコツ

- 読みが複数ある語、英語混じりの表現は**ひらがな読みを併記**するのが望ましい  
  例：  
  ```
  お前らの作った混乱 最後は全てエーアイで俺が始末（しまつ）
  ```
- フレーズごとに**改行**
- セクション（Verse, Hookなど）ごとに**空行**

これにより、Sunoがより正確に音楽化します。

---

## 📦 依存パッケージ

```txt
beautifulsoup4 >= 4.13.4  
mcp[cli] >= 1.7.1  
pandas >= 2.2.3  
requests >= 2.32.3
```

---

## 📁 ディレクトリ構成

```
rap-generator/
├── .gitignore
├── .python-version
├── data/
│   └── in_note_rhymes_compressed.csv
├── prompt/
│   └── custom_prompt.txt
├── pyproject.toml
├── rhyme_mcp_server.py
├── rhyme_scraper.py
├── uv.lock
└── README.md
```