FROM base/archlinux:latest

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

RUN pacman -Syy --noconfirm

RUN pacman -S --noconfirm reflector && reflector --verbose -l 200 -p http --sort rate --save /etc/pacman.d/mirrorlist

RUN pacman -S --noconfirm --needed wget python python-pip vim proxychains base-devel geoip bind-tools grep

RUN cd /tmp && \
    wget https://github.com/kelseyhightower/confd/releases/download/v0.14.0/confd-0.14.0-linux-amd64 -O confd && \
    chmod +x confd

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

ADD docker/confd /etc/confd