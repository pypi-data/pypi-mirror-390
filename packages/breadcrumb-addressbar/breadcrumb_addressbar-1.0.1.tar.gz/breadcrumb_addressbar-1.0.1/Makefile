.PHONY: help install test format lint type-check quality clean build install-dev

help:
	@echo "利用可能なコマンド:"
	@echo "  install     - 依存関係をインストール"
	@echo "  install-dev - 開発用依存関係をインストール"
	@echo "  test        - テストを実行"
	@echo "  format      - コードをフォーマット"
	@echo "  lint        - リントチェック"
	@echo "  type-check  - 型チェック"
	@echo "  quality     - 全体的な品質チェック"
	@echo "  clean       - 一時ファイルを削除"
	@echo "  build       - パッケージをビルド"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install black isort flake8 mypy autopep8 bandit

test:
	pytest tests/ -v

format:
	./scripts/format_code.sh

lint:
	flake8 breadcrumb_addressbar/ examples/ tests/

type-check:
	mypy breadcrumb_addressbar/

quality:
	./scripts/check_code_quality.sh

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build:
	python -m build

# 開発用の便利コマンド
dev-setup: install-dev
	@echo "開発環境のセットアップが完了しました"

quick-test:
	pytest tests/ -v --tb=short

format-check:
	black --check breadcrumb_addressbar/ examples/ tests/
	isort --check-only breadcrumb_addressbar/ examples/ tests/

# CI/CD用
ci-test: format-check lint type-check test
	@echo "CI/CDテストが完了しました"

ci-test-no-cov:
	pytest tests/ -v --tb=short -m "not qt" --disable-pytest-warnings

ci-test-with-cov:
	pytest tests/ -v --tb=short -m "not qt" --disable-pytest-warnings --cov=breadcrumb_addressbar --cov-report=xml --cov-report=term-missing
