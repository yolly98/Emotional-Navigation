MONGO_IMAGE = mongo-smart-navigation
GRAPHHOPPER_IMAGE = graphhopper-smart-navigation
NOMINATIM_IMAGE = nominatim-smart-navigation

run:
	docker run --name ${MONGO_IMAGE} -d -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password -p 27017:27017 mongo
    docker run --name ${GRAPHHOPPER_IMAGE} -d -p 8989:8989 --url https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf --host 0.0.0.0 israelhikingmap/graphhopper
    docker run --name ${NOMINATIM_IMAGE} -d -e PBF_URL=https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf -p 8080:8080  mediagis/nominatim
    python3 script.py

start:
    docker start ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

stop:
    docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

clean:
	docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}
	docker rm ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}