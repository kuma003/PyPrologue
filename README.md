# Prologue

単段 / 多段式ハイブリッドロケットの軌道シミュレーターです.

numpy, pandas, numpy-quaternionのinstallが必須です.  
~conda installではインストールできないので, pipコマンドでインストールしてください.~  
嘘でした. ↓を実行すればインストールできました (参考 : [公式ドキュメント](https://quaternion.readthedocs.io/en/latest/)).
```
conda install -c conda-forge quaternion
```

## memo

1. Geocoordinate.py  
    __degPerLen_latitude, __degPerLen_longitudeの計算が怪しい.
2. Appsettings.py  
    ムリにSingletonにしなくてよかった気がする (可読性が低い). 
