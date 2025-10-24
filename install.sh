#!/bin/bash

# 動画→GIF変換ツール インストールスクリプト

echo "動画→GIF変換ツールのインストールを開始します..."

# Pythonのバージョンチェック
python3 --version
if [ $? -ne 0 ]; then
    echo "エラー: Python3がインストールされていません"
    exit 1
fi

# pipのアップデート
echo "pipをアップデートしています..."
python3 -m pip install --upgrade pip

# 必要なパッケージのインストール
echo "必要なPythonパッケージをインストールしています..."
python3 -m pip install -r requirements.txt

# FFmpegのインストール確認
echo "FFmpegのインストール状況を確認しています..."
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpegがインストールされていません。インストールを開始します..."
    
    # OSの判定
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu系
        sudo apt update
        sudo apt install -y ffmpeg
    elif [ -f /etc/redhat-release ]; then
        # RedHat系
        sudo yum install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "Homebrewがインストールされていません。手動でFFmpegをインストールしてください。"
            echo "https://ffmpeg.org/download.html"
        fi
    else
        echo "このOSはサポートされていません。手動でFFmpegをインストールしてください。"
        echo "https://ffmpeg.org/download.html"
    fi
else
    echo "FFmpegは既にインストールされています。"
fi

# 実行権限の付与
chmod +x gif_converter.py

echo ""
echo "インストールが完了しました！"
echo ""
echo "使用方法:"
echo "  python3 gif_converter.py"
echo ""
echo "または:"
echo "  ./gif_converter.py"
echo ""

