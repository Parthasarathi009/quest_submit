# Makefile for common operations

.PHONY: help setup install test deploy build clean destroy logs

help:
	@echo "Rearc Data Quest - Available Commands"
	@echo "===================================="
	@echo "setup            - Setup Python environment and install dependencies"
	@echo "install          - Install Python dependencies"
	@echo "test             - Run tests"
	@echo "build            - Build Lambda packages"
	@echo "deploy           - Deploy infrastructure with Terraform"
	@echo "destroy          - Destroy AWS infrastructure"
	@echo "logs             - View Lambda logs"
	@echo "clean            - Clean up temporary files"
	@echo ""

setup:
	python -m venv venv
	. venv/bin/activate
	make install

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	@echo "Testing Part 1: BLS Sync..."
	python part_1_s3_sync/sync_bls_data.py
	@echo "Testing Part 2: Population API..."
	python part_2_api/fetch_population_data.py
	@echo "Tests complete!"

build:
	@echo "Building Lambda packages..."
	bash build.sh

deploy:
	@echo "Deploying infrastructure..."
	bash deploy.sh

destroy:
	@echo "Destroying AWS infrastructure..."
	cd part_4_terraform && terraform destroy && cd ..

logs:
	@echo "Combined Lambda logs:"
	aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
	@echo ""
	@echo "Analytics Lambda logs:"
	aws logs tail /aws/lambda/rearc-quest-analytics --follow

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -f *.zip
	rm -rf build/
	rm -rf .terraform/
	rm -f *.tfstate
	rm -f *.tfstate.*
	@echo "Cleanup complete!"

.PHONY: venv
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"
