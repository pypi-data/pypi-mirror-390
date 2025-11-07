#!/bin/bash

# CI環境用テストスクリプト
# BreadcrumbAddressbar プロジェクト用

set -e  # エラー時に停止

echo "🚀 CI環境でのテストを開始します..."

# プロジェクトルートディレクトリに移動
cd "$(dirname "$0")/.."

# 1. 基本的なテスト実行（カバレッジなし）
echo "🧪 基本的なテスト実行中..."
if pytest tests/ -v --tb=short -m "not qt" --disable-pytest-warnings; then
    echo "✅ 基本的なテスト完了"
else
    echo "❌ 基本的なテストでエラーが発生しました"
    exit 1
fi

# 2. カバレッジテスト（利用可能な場合）
echo "📊 カバレッジテスト実行中..."
if python -c "import pytest_cov" 2>/dev/null; then
    echo "📈 pytest-covが利用可能です。カバレッジテストを実行します。"
    if pytest tests/ -v --tb=short -m "not qt" --disable-pytest-warnings --cov=breadcrumb_addressbar --cov-report=xml --cov-report=term-missing; then
        echo "✅ カバレッジテスト完了"
        echo "📁 カバレッジレポート: coverage.xml"
    else
        echo "❌ カバレッジテストでエラーが発生しました"
        exit 1
    fi
else
    echo "⚠️  pytest-covが利用できません。カバレッジテストをスキップします。"
    echo "   インストール: pip install pytest-cov"
fi

# 3. 型チェック（利用可能な場合）
echo "📝 型チェック実行中..."
if command -v mypy &> /dev/null; then
    if mypy breadcrumb_addressbar/; then
        echo "✅ 型チェック完了"
    else
        echo "❌ 型チェックでエラーが発生しました"
        exit 1
    fi
else
    echo "⚠️  mypyが見つかりません。型チェックをスキップします。"
fi

# 4. リントチェック（利用可能な場合）
echo "🔍 リントチェック実行中..."
if command -v flake8 &> /dev/null; then
    if flake8 breadcrumb_addressbar/ examples/ tests/; then
        echo "✅ リントチェック完了"
    else
        echo "❌ リントチェックでエラーが発生しました"
        exit 1
    fi
else
    echo "⚠️  flake8が見つかりません。リントチェックをスキップします。"
fi

echo "✅ CI環境でのテストが完了しました！"
