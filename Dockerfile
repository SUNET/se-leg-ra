FROM debian

MAINTAINER se-leg developers <se-leg@lists.sunet.se>

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /
EXPOSE 5000
VOLUME ["/ra/etc"]

RUN apt-get update && apt-get -yu dist-upgrade
# for troubleshooting in the container
RUN apt-get -y install \
    vim \
    net-tools \
    netcat \
    telnet \
    traceroute
RUN apt-get -y install \
    python-virtualenv \
    git-core \
    gcc \
    python3-dev \
    libssl-dev
# insert additional apt-get installs here
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Dockerfile to the container as documentation
ADD Dockerfile /Dockerfile

# revision.txt is dynamically updated by the CI for every build,
# to ensure the statements below this point are executed every time
ADD docker/revision.txt /revision.txt

ADD . /ra/src

ADD docker/start.sh /start.sh
ADD docker/setup.sh /setup.sh
RUN /setup.sh

CMD ["bash", "/start.sh"]
