.PHONY: run docker-up test demo-data

run:
	python -m energy_app

docker-up:
	docker compose up -d --build

test:
	pytest -q

demo-data:
	python scripts/generate_demo_data.py --output data/sample_consumption.csv
