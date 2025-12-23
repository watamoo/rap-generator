# 🎤 Rap Generator – 日本語ラップ韻検索 & 生成ツール

**Rap Generator**は、日本語ラップの韻を踏んだ歌詞を生成するためのツールです。
韻データをもとに、類似した発音を持つ語句を検索し、Claude Codeでラップを生成できます。

---

## 🚀 セットアップ手順

### リポジトリをクローン

```sh
git clone https://github.com/watamoo/rap-generator.git
cd rap-generator
```

### uvのインストール

Python 3.12以上が必要です。[uv](https://github.com/astral-sh/uv) を使用します。

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 依存関係のインストール

```sh
uv sync
```

---

## 🔧 Claude CodeでMCPサーバを確認

このリポジトリには `.mcp.json` が含まれているため、追加の設定は不要です。

Claude Codeでこのプロジェクトを開き、`/mcp`と入力して、「MCP status」を選択します。
`rap-generator` が一覧に表示されていればOKです。
表示されない場合は、Claude Codeを再起動してください。

Claude Code以外のMCP対応エージェントを使用している場合は、`.mcp.json` を参考にMCPサーバーを設定してください。

---

## 🎤 ラップを生成する

Claude Codeでスラッシュコマンドを使ってラップを生成します：

```
/rap-generator:create_rap テーマ セクション数
```

例：

```
/rap-generator:create_rap 通勤時の満員電車をdisるラップ 4
```

これにより、指定したテーマで韻を踏んだラップ歌詞が生成されます。

---

## 🎧 音楽をつけて歌わせる

1. [Suno](https://suno.com) を開く
2. `Lyrics` にラップ歌詞を入力
3. `Styles` に次の文字列を入力：`aggressive battle rap, rapid-fire flow, hard-hitting punchlines, crisp articulation, tight rhyme scheme`
4. `Create` をクリックして曲を生成

なお、Sunoの無料版では生成できる曲数に制限があるので注意してください。

### ✍️ Suno用の歌詞記述のコツ

- 読みが複数ある語、英語混じりの表現は**ひらがな読みで記載**するのが望ましい
  例：
  ```
  お前らの作った混乱 最後は全てエーアイで俺がしまつ
  ```
- 小節ごとに**改行**
- バースごとに**空行**

これにより、Sunoがより正確にラップしてくれるようになります。
