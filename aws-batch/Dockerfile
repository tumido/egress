FROM centos/python-36-centos7:latest
USER root
RUN yum update -y && yum install postgresql -y && yum clean all -y
RUN pip install --no-cache-dir aws-cli
ADD dump_to_s3.sh /opt/dump_to_s3.sh
WORKDIR /tmp
USER nobody
ENTRYPOINT [ "/opt/dump_to_s3.sh" ]
