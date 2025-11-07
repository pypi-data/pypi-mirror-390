#!/usr/bin/env python3
"""
リリースプロセスを自動化するスクリプト
使用方法: python scripts/release.py <version>
例: python scripts/release.py 1.0.0
"""

import re
import subprocess
import sys
from datetime import datetime


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """コマンドを実行する"""
    print(f"実行中: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"エラー: {result.stderr}")
        sys.exit(1)
    return result


def update_version_in_file(file_path: str, old_version: str, new_version: str) -> None:
    """ファイル内のバージョンを更新する"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # バージョン文字列を置換
    content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"')
    content = content.replace(f'version="{old_version}"', f'version="{new_version}"')
    content = content.replace(f'__version__ = "{old_version}"', f'__version__ = "{new_version}"')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"更新完了: {file_path}")


def update_changelog(version: str) -> None:
    """CHANGELOG.mdを更新する"""
    changelog_path = "CHANGELOG.md"

    # 現在の日付を取得
    today = datetime.now().strftime("%Y-%m-%d")

    # 新しいバージョンエントリを作成
    new_entry = f"## [{version}] - {today}\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n### Removed\n- \n\n"

    # CHANGELOG.mdの内容を読み込み
    with open(changelog_path, encoding="utf-8") as f:
        content = f.read()

    # 新しいエントリを追加（最初の##の前に挿入）
    lines = content.split("\n")
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith("## ["):
            insert_index = i
            break

    lines.insert(insert_index, new_entry.rstrip())

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"更新完了: {changelog_path}")


def main():
    if len(sys.argv) != 2:
        print("使用方法: python scripts/release.py <version>")
        print("例: python scripts/release.py 1.0.0")
        sys.exit(1)
    new_version = sys.argv[1]
    # バージョン形式をチェック
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("エラー: バージョンは x.y.z 形式である必要があります")
        sys.exit(1)
    # 現在のバージョンを取得
    with open("pyproject.toml", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'version = "([^"]+)"', content)
        if not match:
            print("エラー: pyproject.tomlからバージョンを取得できませんでした")
            sys.exit(1)
        old_version = match.group(1)
    print(f"バージョンを {old_version} から {new_version} に更新します")
    # ファイルを更新
    update_version_in_file("pyproject.toml", old_version, new_version)
    update_version_in_file("setup.py", old_version, new_version)
    update_version_in_file("breadcrumb_addressbar/__init__.py", old_version, new_version)
    update_changelog(new_version)
    # テストを実行
    print("\nテストを実行中...")
    run_command("python -m pytest tests/ -v --tb=short")
    # リントを実行
    print("\nリントを実行中...")
    run_command("black --check breadcrumb_addressbar/ tests/ examples/")
    run_command("isort --check-only breadcrumb_addressbar/ tests/ examples/")
    run_command("flake8 breadcrumb_addressbar/ tests/ examples/")
    # ビルドをテスト
    print("\nビルドをテスト中...")
    run_command("python -m build")
    # Gitの状態をチェック
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("\n変更されたファイルがあります:")
        print(result.stdout)
        print("\nコミットしてください:")
        print("git add .")
        print(f"git commit -m 'Bump version to {new_version}'")
        print(f"git tag v{new_version}")
        print("git push origin main --tags")
    else:
        print("\nすべての変更がコミットされています")
        print(f"タグを作成してください: git tag v{new_version}")
        print(f"タグをプッシュしてください: git push origin v{new_version}")


if __name__ == "__main__":
    main()
