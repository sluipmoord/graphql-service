FROM lambci/lambda:build-python3.8
RUN yum -y install postgresql95-devel
