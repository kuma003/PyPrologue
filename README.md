# Prologue

単段 / 多段式ハイブリッドロケットの軌道シミュレーターです.

numpy, pandas, numpy-quaternionのinstallが必須です.  
conda installではインストールできないので, pipコマンドでインストールしてください.

## memo

1. Geocoordinate.py  
    __degPerLen_latitude, __degPerLen_longitudeの計算が怪しい.
2. Appsettings.py  
    ムリにSingletonにしなくてよかった気がする (可読性が低い). 