# Prologue

単段 / 多段式ハイブリッドロケットの軌道シミュレーターです.

## 環境要件
- Python : **ver.3.10以上**[^1]
  (match構文を用いるため)
- numpy
- numpy-quaternion
- pandas
- geopandas (予定)
- plotly (予定)
- kaleido (予定)
[^1]: ver.3.12環境下ではライブラリの競合が発生したので, ver.3.10下を推奨します (2024/9 現在).

Anaconda環境下では次を実行して，必要なライブラリをインストールしてください (参考 : [numpy-quaternion公式ドキュメント](https://quaternion.readthedocs.io/en/latest/)).
```
conda install numpy
conda install -c conda-forge quaternion
conda install pandas
conda install geopandas
conda install plotly
conda install -c conda-forge python-kaleido
```
Colaboratory環境下では次を実行してインストールしてください :
```Python
!pip install numpy-quaternion
!pip install -U kaleido
# ついでに日本語に対応させる (参考:https://qiita.com/siraasagi/items/3836cedede350280ec42)
!apt-get -y install fonts-ipafont-gothic
!rm /root/.cache/matplotlib/fontlist-v300.json
```

## 使い方
PyPrologue自体はColaboratory・ローカル環境問わず動きます (予定).

ローカルで使う場合はトップページの**Code**から**Download ZIP**でPyPrologueをダウンロードし, メインのファイルと同じ階層にPyPrologueフォルダを配置してください.

## memo

1. general  
   ~勘違いでプライベート変数をダブルアンダースコアで表記してたので後でシングルアンダースコアに修正.  
   大抵エラーを生じるので既にある程度は修正済み.~  
   Pythonではprivateがダブルアンダースコア, protectedがシングルアンダースコアの模様.  
   リファクタリング時にどちらかに統一したい.
2. general  
   クラス変数とインスタンス変数の仕様を勘違いしていたため, 後で必ずインスタンス変数として再定義しなおす.
3. Appsettings.py  
   ムリにSingletonにしなくてよかった気がする (可読性が低い). 
4. RocketSpec.py  
   終端速度とCd値の計算式が気になる.
5. RocketSpec.py  
   ```setInfParachuteCd```関数の意図がよくわからない. ChatGPTとも相談したけど抗力係数0のときに初期化したいこと以外の意図不明.  
   本当は自身よりも上のステージの抗力係数だけ足したかった? それならまだ分かるが逆順で足しているのは何故? 
6. WindModel.py  
   getWindFromData関数において, データの最大値よりも高い場合にインデックスをはみ出してしまう.
   外挿したかったが使っているnp.interpの性質上ムリそうなので, 取り合えず最後の値で頭打ちになるようにした.
7.  SimuResult.py  
   毎時間ステップ毎にappendしているので明らかに遅い.
   抜本的にコードを書き換えてリスト内包表記で計算するべき.  
   Organize関数とかもどこかに統合してよい気がする.

## クラス図
クラス図の書き方については[東大の資料](https://lecture.ecc.u-tokyo.ac.jp/hideo-t/references/uml/class-diagram/class-diagram.html)とかが参考になります.
Draw.ioを使って書いているので，書き方は[Draw.io（diagrams.net）で作成したインフラ構成図をコードで管理する、GitHubで編集差分を確認する](https://dev.classmethod.jp/articles/create-infrastructure-diagrams-in-drawio-diactamsnet-manage-them-in-code-and-github/)などを参考にしてください.  
正直クラス図書いててよくわかっていないので, クラス図書ける方適宜修正お願いします.

![クラス図](./docs/class_diagram.drawio.svg)
