# Prologue

単段 / 多段式ハイブリッドロケットの軌道シミュレーターです.

## 環境要件
- Python : **ver.3.10以上**
  (match構文を用いるため)
- numpy
- numpy-quaternion
- pandas
- geopandas (予定)
- plotly (予定)
- kaleido (予定)

Anaconda環境下では次を実行して，必要なライブラリをインストールしてください (参考 : [numpy-quaternion公式ドキュメント](https://quaternion.readthedocs.io/en/latest/)).
```
conda install numpy
conda install -c conda-forge quaternion
conda install pandas
conda install geopandas
conda install plotly
conda install -c conda-forge python-kaleido
```
Colaboratory環境下では上3要件は自動的に満たされているので，次を実行してnumpy-quaternionをインストールしてください :
```{Python}
!pip install numpy-quaternion
```

## 使い方
PyPrologue自体はColaboratory・ローカル環境問わず動きます (予定).

ローカルで使う場合はトップページの**Code**から**Download ZIP**でPyPrologueをダウンロードし, メインのファイルと同じ階層にPyPrologueフォルダを配置してください.

## memo

1. Geocoordinate.py  
   __degPerLen_latitude, __degPerLen_longitudeの計算が怪しい.
2. Appsettings.py  
   ムリにSingletonにしなくてよかった気がする (可読性が低い). 
3. RocketSpec.py  
   終端速度とCd値の計算式が気になる.
4. RocketSpec.py
   ```setInfParachuteCd```関数の意図がよくわからない. ChatGPTとも相談したけど抗力係数0のときに初期化したいこと以外の意図不明.  
   本当は自身よりも上のステージの抗力係数だけ足したかった? それならまだ分かるが逆順で足しているのは何故? 
