# プロジェクト構造

## ディレクトリ構成

```
パンくずリスト型アドレスバー/
├── breadcrumb_addressbar/          # メインライブラリパッケージ
│   ├── __init__.py                # パッケージエクスポートとバージョン情報
│   ├── core.py                    # BreadcrumbAddressBarメインウィジェット
│   ├── widgets.py                 # BreadcrumbItemとヘルパーウィジェット
│   ├── popup.py                   # FolderSelectionPopup実装
│   ├── themes.py                  # ThemeManagerとテーマ統合
│   └── logger_setup.py            # ログ設定ユーティリティ
├── tests/                         # テストスイート
│   ├── __init__.py
│   └── test_core.py              # コア機能テスト
├── examples/                      # 使用例とデモ
│   ├── basic_example.py          # シンプルな統合例
│   ├── qt_theme_demo.py          # テーマ統合デモ
│   ├── phase2_example.py         # 高度な機能デモ
│   └── dropdown_test*.py         # WSL2互換性テスト
├── docs/                         # ドキュメント
│   └── BreadcrumbAddressBar.md   # 詳細仕様
├── .kiro/                        # Kiro AIアシスタント設定
│   └── steering/                 # AIガイダンス文書
└── venv*/                        # 仮想環境（gitignore対象）
```

## コード構成原則

### モジュール責務
- **core.py**: メインBreadcrumbAddressBarウィジェット、パス処理、表示ロジック
- **widgets.py**: 個別パンくずボタンコンポーネント（BreadcrumbItem）
- **popup.py**: フォルダ選択ポップアップ機能
- **themes.py**: テーマ管理とqt-theme-manager統合
- **logger_setup.py**: 集約ログ設定

### インポート構造
```python
# 標準ライブラリインポートを最初に
import os
from typing import Any, Dict, List, Optional

# サードパーティインポートを次に
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

# ローカルインポートを最後に
from .logger_setup import get_logger
from .widgets import BreadcrumbItem
```

## 命名規則

### ファイルとディレクトリ
- **snake_case**: 全てのファイルとディレクトリ名
- **説明的な名前**: 明確な目的を示す（例：`logger_setup.py`）

### コード要素
- **クラス**: PascalCase（例：`BreadcrumbAddressBar`、`FolderSelectionPopup`）
- **メソッド/関数**: パブリックAPIはcamelCase、内部はsnake_case
- **変数**: ローカルはcamelCase、プライベートはアンダースコア接頭辞付きsnake_case
- **定数**: UPPER_SNAKE_CASE

### 一時/デバッグコード
- **デバッグ関数**: `_debug_`接頭辞（PR前に削除必須）
- **一時変数**: `_temp_`接頭辞と明確なクリーンアップ計画

## 設定ファイル

### パッケージ設定
- **pyproject.toml**: モダンなPythonプロジェクトメタデータ、依存関係、ツール設定
- **setup.py**: 従来互換性とパッケージビルド

### 開発設定
- **.cursorrules**: プロジェクト固有の開発ガイドライン
- **.gitignore**: バージョン管理除外
- **pytest設定**: pyproject.tomlの`[tool.pytest.ini_options]`内

## テスト構造
- **ユニットテスト**: `tests/test_*.py`パターン
- **テストクラス**: メインクラス構造をミラー（`TestBreadcrumbAddressBar`）
- **フィクスチャ**: `setup()`メソッドでのQtアプリケーションセットアップ
- **テスト命名**: 説明的なテストメソッド名（`test_path_changed_signal`）

## ドキュメント構造
- **README.md**: 例付きユーザー向けドキュメント
- **USAGE.md**: 詳細な使用方法とトラブルシューティング
- **docs/**: 技術仕様と設計文書
- **CHANGELOG.md**: バージョン履歴と変更点

## ビルド成果物（gitignore対象）
- **venv/**, **venv_windows/**: 仮想環境
- **__pycache__/**: Pythonバイトコードキャッシュ
- **.mypy_cache/**: 型チェックキャッシュ
- **breadcrumb_addressbar.egg-info/**: パッケージメタデータ
- **build/**, **dist/**: パッケージビルド出力
