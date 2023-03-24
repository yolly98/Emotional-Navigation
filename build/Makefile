SQL_IMAGE = mysql-smart-navigation
GRAPH_IMAGE = neo4j_smart_navigation
GRAPH_DOCKERFILE = Dockerfile

build:
	docker build -f ${GRAPH_DOCKERFILE} -t ${GRAPH_IMAGE} .

run:
	docker run --name ${GRAPH_IMAGE} -p 7474:7474 -p 7687:7687 -d --env NEO4J_AUTH=neo4j/password ${GRAPH_IMAGE}
	docker run --name ${SQL_IMAGE} -p 3306:3306 -d -e "MYSQL_ROOT_PASSWORD=password" mysql

clean:
	docker stop ${SQL_IMAGE} ${GRAPH_IMAGE}
	docker rm ${SQL_IMAGE} ${GRAPH_IMAGE}