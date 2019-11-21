FROM postgres:latest
ADD dump_to_s3.sh /opt/dump_to_s3.sh
WORKDIR /tmp
USER nobody
ENTRYPOINT [ "/opt/dump_to_s3.sh" ]
