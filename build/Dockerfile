# note: update the apoc version in the link if it doesn't work

FROM neo4j:latest
RUN echo 'dbms.transaction.timeout=60s' >> /var/lib/neo4j/conf/neo4j.conf
RUN wget -P plugins https://github.com/neo4j/apoc/releases/download/5.6.0/apoc-5.6.0-core.jar
