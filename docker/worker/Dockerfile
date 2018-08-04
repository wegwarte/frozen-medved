FROM medved_base:latest

RUN pacman -S --noconfirm --needed git libpcap linux-headers clang tor

RUN git clone https://github.com/robertdavidgraham/masscan && \
    cd masscan && \
    make -j && \
    mv bin/masscan /usr/bin/masscan

RUN wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz && gunzip GeoLiteCity.dat.gz

RUN mkdir -p /usr/share/GeoIP/ && mv GeoLiteCity.dat /usr/share/GeoIP/GeoIPCity.dat

ADD files/run.sh /tmp/run.sh

CMD ["/tmp/run.sh"]
