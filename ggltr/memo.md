# pdfminer

## pdfminer.pdfdocument.PDFTextExtractionNotAllowed:
PDFが「編集可能」という状態じゃないと読み取れない。
[zpdf](https://sourceforge.net/projects/qpdf/)で編集可能にする。

### コマンド
D:\～～>C:\～～\qpdf-8.4.0\bin\qpdf.exe --decrypt 元ファイル.pdf 出力ファイル.pdf

# googletrans

## proxy
* まだ対応してないと書いてある。。。[ここ](https://github.com/ssut/py-googletrans)
* os.environ['https_proxy'] にセットすれば大丈夫♪
* catchするエラーは「requests.exceptions.ConnectionError」

## json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
* googleがブロック、ということらしい。
* time.sleep(x) で待って何度かtryにしてみる。
* catchするエラーは「json.decoder.JSONDecodeError」

proxyないとこだと一度ダメになると全然ダメ。(2019.4.7)
　-> 他の方法を考えるor調べる。。。
