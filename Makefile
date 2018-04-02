all: down clean base bup

base:
	docker build -t medved_base .

basenc:
	docker build -t medved_base . --no-cache

up:
	docker-compose up

upd:
	docker-compose up -d

bup:
	docker-compose up --build

bupd:
	docker-compose up --build -d

bupds:
	docker-compose up --build -d --scale worker=5

down:
	docker-compose down

test:
	docker build -t medved_base_test -f Dockerfile.test .

clean:
	find -iname *.pyc -delete
	find -type d -name __pycache__ -delete
	sudo rm -vf *.log 
	sudo rm -f config.json

cleandb:
	sudo rm -rfv docker/lib/mongo/*
	sudo rm -rfv docker/lib/redis/*
