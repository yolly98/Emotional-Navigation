MONGO_IMAGE = mongo-smart-navigation
GRAPH_IMAGE = neo4j-smart-navigation
GRAPH_DOCKERFILE = Dockerfile

build:
	docker build -f ${GRAPH_DOCKERFILE} -t ${GRAPH_IMAGE} .

run:
	docker run --name ${GRAPH_IMAGE} -p 7474:7474 -p 7687:7687 -d --env NEO4J_AUTH=neo4j/password ${GRAPH_IMAGE}
	docker run --name ${MONGO_IMAGE} -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password -p 27017:27017 -d mongo

clean:
	docker stop ${MONGO_IMAGE} ${GRAPH_IMAGE}
	docker rm ${MONGO_IMAGE} ${GRAPH_IMAGE}