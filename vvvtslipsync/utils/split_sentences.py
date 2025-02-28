from re import split

def split_sentences(text):
    # 正規表現パターン：句点、疑問符、感嘆符、改行で分割
    pattern = r'(?<=[。？！])|\r?\n'
    # 正規表現で分割し、リストに格納
    sentences = split(pattern, text)
    # 空の要素を削除
    sentences = [sentence for sentence in sentences if sentence]
    return sentences
