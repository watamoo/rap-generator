# rhyme_server.py
from pathlib import Path
import random
from typing import List, Tuple

import pandas as pd
from mcp.server.fastmcp import FastMCP

# --------------------------------------------------
# データ読み込み
# --------------------------------------------------
if Path("data/in_note_rhymes.csv").exists():
    DATA_PATH = Path("data/in_note_rhymes.csv")
else:
    DATA_PATH = Path("data/in_note_rhymes_compressed.csv")  # 全データのcsvがない場合は圧縮版を使用

df = pd.read_csv(DATA_PATH)

# target_word ➜ [(rhyme_word, reading, n_chars), ...]
_rhyme_dict = {
    target: list(zip(g["rhyme_word"], g["reading"], g["n_chars"])) for target, g in df.groupby("target_word", sort=False)
}

# --------------------------------------------------
# MCP サーバ初期化
# --------------------------------------------------
mcp = FastMCP("rhyme_server")


@mcp.tool()
def get_rhymes(word: str, top_k: int | None = 100) -> List[Tuple[str, str]]:
    """
    指定した単語と韻を踏める候補 (rhyme_word, reading) を返す。

    ソート規則:
        1. 文字数が多い順
        2. 同じ文字数の単語間はランダム抽出

    Args:
    word (str): インプット単語。ひらがなに直さず、元々の単語で指定する

        top_k (int | None, optional): 返す最大件数。None で全件

    Returns:
        List[Tuple[str, str]]: (rhyme_word, reading) のタプル列。
                               該当がなければ空リスト。
    """
    candidates = _rhyme_dict.get(word, [])
    if not candidates:
        return []

    # シャッフルしてから n_chars で降順ソート
    random.shuffle(candidates)
    candidates.sort(key=lambda x: x[2], reverse=True)  # x[2] は n_chars

    # n_chars を落として (word, reading) だけ返す
    result = [(w, r) for w, r, _ in candidates]
    return result[:top_k] if top_k is not None else result


@mcp.tool()
def get_available_words(n: int = 100) -> List[str]:
    """
    韻データベースの中から、対応可能な target_word をランダムに選んで返す。

    条件:
        - 対応する rhyme_word が10個以上あるもののみ対象
        - ランダム抽出
        - デフォルトは最大100件

    Args:
        n (int): 返す単語数の上限（デフォルト100）

    Returns:
        List[str]: 韻データの対象になっている target_word のリスト
    """
    valid_targets = [t for t, rhymes in _rhyme_dict.items() if len(rhymes) >= 10]
    return random.sample(valid_targets, min(n, len(valid_targets)))


@mcp.prompt()
def create_rap(theme: str, num_section: int = 4) -> str:
    """
    ラップ歌詞を生成するプロンプトテンプレート。

    Args:
        theme (str): ラップのテーマ
        num_section (int): 生成するセクション数（デフォルト4）

    Returns:
        str: プロンプトテンプレート文字列
    """
    prompt = f"""
    あなたはプロフェッショナルなラッパーとして、提示されたテーマに基づき、高品質かつ韻律の整ったラップ歌詞を生成せよ。  
    以下の手順・条件を**一字一句守り**、情報を欠落させずに構造化したフローで進行せよ。

    ## テーマ
    {theme}


    ## 使用ツール
    - **`rhyme_search.get_available_words`**  
    テーマに対して韻を踏める可能性がある単語リストを取得する。
    - **`rhyme_search.get_rhymes`**  
    指定単語（ひらがな5文字以上）と韻を踏める単語を検索する。

    ## ラップ生成フロー

    ### 1️⃣ 単語リスト取得 & キーワード選定
    1. `get_available_words`で韻候補リストを取得。n=300として多くの単語を確認。  
    2. リストから**テーマに沿ったフレーズが作れそうな単語を1語**選び、  
    - その単語がテーマに合致している理由を**3行で説明**。  
    - 韻候補リストに記載してある単語全体を採用するように注意せよ。

    ### 2️⃣ 最初のラップフレーズ生成
    3. 選定した単語を省略・変形させることなく**語尾**に据え、短い最初のフレーズを生成。  
    - 例: 「俺はHIPHOP生まれHIPHOP育ち」「優勝したくらいで男泣き？」  
    - **セルフボーストやディス要素**を適度に入れる。  
    - フレーズ長は例示レベル（1文）に収める。 ビートの1小節で収まるような長さにする 

    ### 3️⃣ 韻検索 & 次フレーズ用単語選定
    4. ステップ2で使った単語を `get_rhymes` で検索。n=100として多くの単語を確認。    
    5. 結果から**最大3語**まで、  
    - テーマや直前フレーズとの意味的つながりを考慮して選定。 
    - あまり一般的でない用語だと伝わらないリスクもあるので避ける。
    - 単語と、ひらがなでのその読みをセットで出力 
    - 選定理由（テーマへの適合性）を**各3行で説明**。  
    6. **適切な韻が無い場合**    
    - ステップ1のキーワードを選定し直す。

    ### 4️⃣ 韻を踏む追加フレーズ生成
    7. ステップ5で選んだ各単語について  
    1. まず「どう単語を使って意味を繋げるか」の方法を簡潔に説明。  
    2. その後、連続性を保ちつつ韻を踏む**1行フレーズ**を生成。
    -  最初のフレーズと同じく、ビートの1小節で収まるような長さにすること。
    -  それまでのフレーズとのつながりよりも、1行フレーズの中で、語尾の単語につながる必然性が伝わるフレーズにする。 

    ### 5️⃣ 次セクションへ
    8. ステップ1〜4を**最大{num_section}セクション**繰り返す。  
    - 各セクション開始時に `get_available_words` を再実行し、新規単語を選定する。  

    ### 6️⃣ フレーズ全体の統一・最終出力
    9. 生成した全フレーズを見直し、  テーマ・意味・リズムの一貫性を調整
    - とくに、フレーズが長くなっているものは、韻に関係ない前半を切り詰める（目安は25文字以内）
    - 韻が踏めていない／単語ヒットしなかったフレーズは**除外**。
    10. 全体を見直し、フレーズ末尾以外の部分での押韻を検討。
    - 韻を踏むならひらがな5文字以上の名詞である必要があるため、その前提で韻候補を探す
    - 適宜  `get_rhymes`を利用して、うまく韻で繋げられそうな部分は歌詞を変更する。
    - 韻をつなげる場合は、隣接するフレーズの同じ場所に入れ込むようにすること。
    - 少しでも多く韻を入れられるよう貪欲に取り組むこと。
    - 検討結果として修正した箇所を出力
    11. **調整後の歌詞だけ**を最終アウトプットとして提示。
    - フレーズ内にはスペースを空けず、フレーズ間は1行空けて出力。セクションの間は空行を入れるようにしてください

    ## 最終アウトプット形式例（内容は関係ないので無視してください）
    ```
    頭使えよ筋肉バカどもxxxxx 
    知識ゼロの筋肉バカに教えるxxxxx
    文化の光で無知を照らす我らxxxxx
    言葉の力で頭を破壊xxxxx

    筋肉じゃなく知性で勝負だxxxxx
    成績トップ 運動バカとは大違いxxxxx
    知識の戦いじゃお前ら敗北xxxxx
    頭使えば人生変わるぜxxxxx
    ・・・・・
    ```

    --------------------------------------------------------------------
    ## 作詞ガイドライン（常時遵守）
    - **セルフボースト & ディス**でインパクトを演出。  
    - たまに **ey / yeah / yo** など英語表現を差し込んで、フローを強調。  
    - **フロー・グルーヴ重視**：リズム感ある語彙を選択。  
    - **反復表現・オノマトペ**を効果的に挿入し、耳に残る仕上がりに。  

    --------------------------------------------------------------------
    ### 📌 例示フレーズ（長さの目安）
    - 「俺はHIPHOP生まれHIPHOP育ち」  
    - 「こいつを倒せば前人未到」  
    - 「振り返るとお前の帰る方向」  

    上記フロー・ガイドラインを厳守し、テーマに沿った高品質ラップを完成させよ。
    """

    return prompt


# --------------------------------------------------
# エントリポイント
# --------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
