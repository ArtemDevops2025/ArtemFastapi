FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "tzdata tzdata/Areas select Europe" > /tmp/tzdata.txt && \
    echo "tzdata tzdata/Zones/Europe select Berlin" >> /tmp/tzdata.txt && \
    debconf-set-selections /tmp/tzdata.txt

RUN apt-get update && \
    apt-get install -y openssh-server passwd sudo iproute2 git curl iputils-ping net-tools wget python3 python3-pip tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install fastapi uvicorn pandas

RUN useradd --create-home -s /bin/bash vagrant && \
    echo 'vagrant:vagrant' | chpasswd && \
    echo 'vagrant ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/vagrant && \
    chmod 440 /etc/sudoers.d/vagrant

RUN mkdir -p /home/vagrant/.ssh && \
    chmod 700 /home/vagrant/.ssh
ADD https://raw.githubusercontent.com/hashicorp/vagrant/master/keys/vagrant.pub /home/vagrant/.ssh/authorized_keys
RUN chmod 600 /home/vagrant/.ssh/authorized_keys && \
    chown -R vagrant:vagrant /home/vagrant/.ssh

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir /var/run/sshd

WORKDIR /app

COPY main.py .
COPY questions.csv .

EXPOSE 22 80

CMD /usr/sbin/sshd -D & uvicorn main:app --host 0.0.0.0 --port 80