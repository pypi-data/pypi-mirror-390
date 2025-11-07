# リリース手順

このドキュメントでは、BreadcrumbAddressbarプロジェクトのリリース手順を説明します。

## 前提条件

1. PyPIアカウントを持っていること
2. GitHubリポジトリにアクセス権限があること
3. GitHub SecretsにPyPI APIトークンが設定されていること

## PyPI APIトークンの設定

### 1. PyPIでAPIトークンを生成

1. [PyPI](https://pypi.org)にログイン
2. Account Settings → API tokens → Add API token
3. トークン名を入力（例: `breadcrumb-addressbar-release`）
4. Scopeを「Entire account (all projects)」に設定
5. トークンをコピー（一度しか表示されません）

### 2. GitHub Secretsに設定

1. GitHubリポジトリのSettings → Secrets and variables → Actions
2. "New repository secret"をクリック
3. Name: `PYPI_API_TOKEN`
4. Value: コピーしたAPIトークン
5. "Add secret"をクリック

## リリース手順

### 1. リリーススクリプトを使用（推奨）

```bash
# 新しいバージョンを指定してリリーススクリプトを実行
python scripts/release.py 1.0.0
```

このスクリプトは以下を自動実行します：
- バージョン番号の更新（pyproject.toml, setup.py）
- CHANGELOG.mdの更新
- テストの実行
- リントチェック
- ビルドテスト

### 2. 手動でのリリース

#### 2.1 バージョン更新

```bash
# pyproject.tomlとsetup.pyのバージョンを更新
# 例: 0.2.0 → 1.0.0
```

#### 2.2 CHANGELOG.md更新

```bash
# CHANGELOG.mdに新しいバージョンのエントリを追加
```

#### 2.3 テスト実行

```bash
# テストを実行
pytest tests/ -v

# リントチェック
black --check breadcrumb_addressbar/ tests/ examples/
isort --check-only breadcrumb_addressbar/ tests/ examples/
flake8 breadcrumb_addressbar/ tests/ examples/
```

#### 2.4 コミットとタグ作成

```bash
# 変更をコミット
git add .
git commit -m "Bump version to 1.0.0"

# タグを作成
git tag v1.0.0

# プッシュ
git push origin main
git push origin v1.0.0
```

## 自動リリース

GitHub Actionsが自動的に以下を実行します：

1. **テスト実行**: 全Pythonバージョン（3.12-3.12）でテスト
2. **リントチェック**: black, isort, flake8
3. **ビルド**: パッケージのビルド
4. **PyPI公開**: ビルドされたパッケージをPyPIにアップロード
5. **GitHub Release**: リリースノートとアーティファクトの作成

## リリース後の確認

1. [PyPI](https://pypi.org/project/breadcrumb-addressbar/)でパッケージが公開されていることを確認
2. GitHubのReleasesページでリリースが作成されていることを確認
3. インストールテスト：

```bash
pip install breadcrumb-addressbar==1.0.0
```

## トラブルシューティング

### よくある問題

1. **APIトークンエラー**
   - GitHub Secretsの設定を確認
   - トークンの権限を確認

2. **ビルドエラー**
   - MANIFEST.inの設定を確認
   - 依存関係の設定を確認

3. **テストエラー**
   - ローカルでテストを実行して確認
   - 依存関係のバージョンを確認

### ロールバック

リリースに問題がある場合：

1. PyPIからパッケージを削除（可能な場合）
2. GitHub Releaseを削除
3. タグを削除：`git tag -d v1.0.0`
4. リモートタグを削除：`git push origin :refs/tags/v1.0.0`

## セマンティックバージョニング

- **MAJOR**: 互換性のない変更
- **MINOR**: 後方互換性のある新機能
- **PATCH**: 後方互換性のあるバグ修正

例：
- 0.2.0 → 1.0.0: メジャーリリース
- 1.0.0 → 1.1.0: マイナーリリース
- 1.1.0 → 1.1.1: パッチリリース
