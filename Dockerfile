# Docker file for a slim Ubuntu-based Python3 image

FROM ubuntu:latest
LABEL maintainer="alan@praktikos.com"

# https://websiteforstudents.com/installing-the-latest-python-3-7-on-ubuntu-16-04-18-04/
RUN apt-get update 
RUN apt-get install -y apt-utils 
RUN apt-get update \
  && apt-get install -y software-properties-common vim \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update -y \
  && apt-get install -y build-essential python3.7 python3-pip python3-venv \
  && ln -s /usr/bin/python3 /usr/local/bin/python \
  && ln -s /usr/bin/pip3 /usr/local/bin/pip \
  && pip3 install pytest


RUN apt-get update

ENTRYPOINT ["python3"]

RUN apt-get install -y wget tar git openssh-server openssh-client ca-certificates nano

# To add the apt repository, first create the file /etc/apt/sources.list.d/pgdg.list, and add a line for the repository as per your distribution.
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

# Then import the repository signing key, and update the system package lists like this.
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# RUN apt-key adv--keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# https://askubuntu.com/questions/831292/how-do-i-install-postgresql-9-6-on-any-ubuntu-version
RUN apt-get install -y software-properties-common
RUN add-apt-repository "deb https://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main"
RUN apt-get update -y

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y tzdata
RUN apt-get install -y postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6 postgresql-server-dev-9.6

# https://stackoverflow.com/questions/25845538/how-to-use-sudo-inside-a-docker-container
RUN apt-get update && \
      apt-get -y install sudo

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

RUN echo "host all  all	0.0.0.0/0  md5" >> /etc/postgresql/9.6/main/pg_hba.conf
RUN cat /etc/postgresql/9.6/main/pg_hba.conf | sed 's/peer/trust/g' >> /etc/postgresql/9.6/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.6/main/postgresql.conf

USER postgres
RUN /etc/init.d/postgresql start \
    && psql -c "CREATE DATABASE praktikos_test;" \
    && psql -c 'GRANT ALL PRIVILEGES ON DATABASE praktikos_test TO postgres;' \
    && psql -c 'CREATE EXTENSION hstore;' praktikos_test \
    && /etc/init.d/postgresql restart

# RUN mkdir -p /var/lib/postgresql/.aws

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of databases
VOLUME ["/var/lib/postgresql"]

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/9.6/bin/postgres", "-D", "/var/lib/postgresql", "-c", "config_file=/etc/postgresql/9.6/main/postgresql.conf"]

WORKDIR /mnt
USER root

# Define default command.
CMD ["bash"]
