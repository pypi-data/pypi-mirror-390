#!/bin/bash

# コード品質チェックスクリプト
# BreadcrumbAddressbar プロジェクト用

set -e  # エラー時に停止

echo "🔍 コード品質チェックを開始します..."

# プロジェクトルートディレクトリに移動
cd "$(dirname "$0")/.."

# 1. 型チェック
echo "📝 型チェック中..."
if command -v mypy &> /dev/null; then
    if mypy breadcrumb_addressbar/; then
        echo "✅ 型チェック完了（エラーなし）"
    else
        echo "❌ 型チェックでエラーが見つかりました"
        exit 1
    fi
else
    echo "⚠️  mypyが見つかりません。インストールしてください: pip install mypy"
fi

# 2. リントチェック
echo "🔍 リントチェック中..."
if command -v flake8 &> /dev/null; then
    if flake8 breadcrumb_addressbar/ examples/ tests/; then
        echo "✅ リントチェック完了（エラーなし）"
    else
        echo "❌ リントチェックでエラーが見つかりました"
        exit 1
    fi
else
    echo "⚠️  flake8が見つかりません。インストールしてください: pip install flake8"
fi

# 3. テスト実行
echo "🧪 テスト実行中..."
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short; then
        echo "✅ テスト完了（全テスト通過）"
    else
        echo "❌ テストでエラーが見つかりました"
        exit 1
    fi
else
    echo "⚠️  pytestが見つかりません。インストールしてください: pip install pytest"
fi

# 4. カバレッジチェック
echo "📊 カバレッジチェック中..."
if command -v pytest &> /dev/null; then
    if pytest tests/ --cov=breadcrumb_addressbar --cov-report=html --cov-report=term-missing --cov-report=xml; then
        echo "✅ カバレッジチェック完了"
        echo "📁 カバレッジレポート: htmlcov/index.html"
        echo "📁 XMLレポート: coverage.xml"
    else
        echo "❌ カバレッジチェックでエラーが見つかりました"
        exit 1
    fi
else
    echo "⚠️  pytestが見つかりません。インストールしてください: pip install pytest pytest-cov"
fi

# 5. セキュリティチェック（オプション）
echo "🔒 セキュリティチェック中..."
if command -v bandit &> /dev/null; then
    if bandit -r breadcrumb_addressbar/; then
        echo "✅ セキュリティチェック完了（問題なし）"
    else
        echo "⚠️  セキュリティチェックで問題が見つかりました"
    fi
else
    echo "ℹ️  banditが見つかりません。セキュリティチェックをスキップします"
    echo "   インストール: pip install bandit"
fi

echo "✅ コード品質チェックが完了しました！"
