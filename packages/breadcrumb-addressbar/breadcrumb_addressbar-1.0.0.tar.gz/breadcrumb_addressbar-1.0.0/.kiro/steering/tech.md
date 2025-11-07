# 技術スタック

## コア技術
- **Python**: 3.12以上（3.12、3.13、3.14をサポート）
- **PySide6**: 主要なQtバインディング（6.0.0以上）
- **qt-theme-manager**: テーマ統合（0.2.0以上または1.0.0以上）

## ビルドシステム
- **setuptools**: パッケージビルドと配布
- **pyproject.toml**: モダンなPythonプロジェクト設定
- **setup.py**: パッケージメタデータの従来互換性

## 開発依存関係
- **pytest**: テストフレームワーク（6.0以上）
- **pytest-qt**: Qt固有のテストユーティリティ（4.0以上）
- **black**: コードフォーマット（22.0以上）
- **flake8**: リンティング（4.0以上）
- **isort**: インポート整理

## 共通コマンド

### 開発環境セットアップ
```bash
# リポジトリをクローンして開発環境をセットアップ
git clone <repo-url>
cd BreadcrumbAddressbar
python -m venv venv
venv\Scripts\activate  # Windows
pip install -e ".[dev]"
```

### テスト
```bash
# 全テストを実行
pytest

# 詳細出力でテストを実行
pytest -v

# 特定のテストファイルを実行
pytest tests/test_core.py
```

### コード品質
```bash
# コードをフォーマット
black .
isort .

# コードをリント
flake8 breadcrumb_addressbar/ tests/ examples/
```

### パッケージビルド
```bash
# パッケージをビルド
python -m build

# 開発モードでインストール
pip install -e .
```

### サンプル実行
```bash
# 基本サンプル
python examples/basic_example.py

# テーマデモ
python examples/qt_theme_demo.py

# フェーズ2機能デモ
python examples/phase2_example.py
```

## アーキテクチャパターン
- **Qt Signal/Slot**: 主要な通信メカニズム
- **ウィジェット構成**: BreadcrumbAddressBarがBreadcrumbItemウィジェットを含む
- **テーママネージャー統合**: qt-theme-manager経由のプラガブルテーマシステム
- **ログ**: Pythonログモジュール経由の構造化ログ（print文は使用しない）

## プラットフォーム考慮事項
- **パス処理**: クロスプラットフォームパス正規化（/ vs \\）
- **Qt互換性**: PySide6が主要、将来のPyQt6互換性を考慮した設計
- **WSL2制限**: WSL2環境でのQComboBoxドロップダウンの既知の問題
