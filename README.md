# VoiceVox VTubeStudio Lipsync


VOICEVOXの音声合成APIを使用して生成された音声データに基づいて、VTubeStudioのキャラクターの口の動きを制御するためのサンプルアプリケーション。


## セットアップ

```powershell
git clone https://github.com/oaiwej/vvvtslipsync.git
cd vvvtslipsync
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## テスト

音声データのレスポンスと同時に口を動かすプログラムです。

1. VOICEVOXとVTubeStudioを起動しておきます。
1. `python -m vvvtslipsync`を実行します。
1. 別窓から`/speak`エンドポイントにPOSTリクエストを送信し、レスポンスと同時に再生開始します。

    ```powershell
    curl -X POST "http://localhost:8000/speak" -H "Content-Type: application/json" -d '{"text": "VOICEVOXとブイチューブスタジオのリップシンク連携テストをしています。口の動きは合っていますか？声とズレていたりしないでしょうか？", "speaker_id": 10 }' --output '.\test.wav'; (New-Object System.Media.SoundPlayer (Get-Item '.\test.wav')).PlaySync();
    ```

1. VOICEVOXで生成された音声が再生され、VTubeStudioのキャラクターの口が動きます。
