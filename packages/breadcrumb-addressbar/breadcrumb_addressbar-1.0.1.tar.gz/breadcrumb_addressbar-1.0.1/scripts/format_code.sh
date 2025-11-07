#!/bin/bash

# コードフォーマット自動化スクリプト
# BreadcrumbAddressbar プロジェクト用

set -e  # エラー時に停止

echo "🔧 コードフォーマットを開始します..."

# プロジェクトルートディレクトリに移動
cd "$(dirname "$0")/.."

# 1. isortでimportを整理
echo "📦 importを整理中..."
if command -v isort &> /dev/null; then
    isort breadcrumb_addressbar/ examples/ tests/
    echo "✅ isort完了"
else
    echo "⚠️  isortが見つかりません。インストールしてください: pip install isort"
fi

# 2. blackでコードフォーマット
echo "⚫ blackでフォーマット中..."
if command -v black &> /dev/null; then
    black breadcrumb_addressbar/ examples/ tests/
    echo "✅ black完了"
else
    echo "⚠️  blackが見つかりません。インストールしてください: pip install black"
fi

# 3. autopep8で追加の修正
echo "🔧 autopep8で追加修正中..."
if command -v autopep8 &> /dev/null; then
    autopep8 --in-place --recursive --aggressive --aggressive breadcrumb_addressbar/ examples/ tests/
    echo "✅ autopep8完了"
else
    echo "⚠️  autopep8が見つかりません。インストールしてください: pip install autopep8"
fi

# 4. flake8でリントチェック
echo "🔍 リントチェック中..."
if command -v flake8 &> /dev/null; then
    if flake8 breadcrumb_addressbar/ examples/ tests/; then
        echo "✅ flake8チェック完了（エラーなし）"
    else
        echo "❌ flake8でエラーが見つかりました"
        exit 1
    fi
else
    echo "⚠️  flake8が見つかりません。インストールしてください: pip install flake8"
fi

echo "✅ コードフォーマットが完了しました！"
