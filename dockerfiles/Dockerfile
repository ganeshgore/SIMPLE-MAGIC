FROM ubuntu:18.04

MAINTAINER Ganesh Gore<goreganesh007@gmail.com>

ENV NUM_CORES 4
ENV DEBIAN_FRONTEND=noninteractive

USER root

# Update debian and clean cache
RUN apt-get update -qq -y 
RUN apt-get -y install wget build-essential git-core curl unzip\
    && apt-get -y install python-tk git-core libreadline-dev \
    && apt-get -y install python python2.7-dev python-pip python-matplotlib python-numpy python-scipy

RUN pip install --upgrade pip 
RUN pip install pandas svgwrite
	
# Install Z3 in docker container 
COPY installers/z3-master.zip /tmp/
RUN cd /tmp/ \
    && unzip z3-master.zip \
    && cd z3-master \
    && python scripts/mk_make.py --python \
    && cd build \
    && make \
    && make install \
    && cd / \
    && rm -rf /tmp/z3-master z3-master.zip

# Install ABC Tool in Docker Container
COPY installers/abc-master.zip /tmp/

RUN cd /tmp/ \
    && unzip abc-master.zip \
    && cd abc-master \
    && make clean \
    && make \
    && rm -rf abc-master.zip

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /simple-magic
