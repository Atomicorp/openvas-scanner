FROM kalilinux/kali-linux-docker

MAINTAINER support <support@atomicorp.com>

#RUN sed -i 's/^# deb-src \(.*xenial.* main restricted\)$/deb-src \1/g' /etc/apt/sources.list
RUN echo "deb http://http.kali.org/kali kali-rolling main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src http://http.kali.org/kali kali-rolling main contrib non-free" >> /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get install wget

RUN wget http://www.atomicorp.com/RPM-GPG-KEY.art.txt
RUN  cat RPM-GPG-KEY.atomicorp.txt | apt-key add - 

# Adding atomic repo 
#RUN echo "deb http://10.66.6.13/channels/atomic/ubuntu/ kali main" >> /etc/apt/sources.list 

# Adding atomic-testing repo 
RUN echo "deb http://10.66.6.13/channels/atomic-testing/ubuntu/ kali main" >> /etc/apt/sources.list 

# Adding atomic-bleeding repo 
#RUN echo "deb http://10.66.6.13/channels/atomic-bleeding/ubuntu/ kali main" > /etc/apt/sources.list 

RUN apt-get update

#RUN apt-get build-dep -y linux 
RUN apt-get install -y fakeroot devscripts bc  debhelper bison cmake doxygen libgcrypt-dev libglib2.0-dev libgnutls28-dev libgpgme11-dev libhiredis-dev libksba-dev libldap2-dev libpcap-dev libssh-dev uuid-dev libsnmp-dev
RUN apt-get install -y libopenvas-dev openvas-nasl

RUN apt-get clean 

RUN install --directory -m 0755 /data && \
    install --directory -m 0755 /patches


WORKDIR /data

VOLUME /data
VOLUME /patches

RUN groupadd -r gitlab-runner -g 478
RUN useradd -u 480 -r -g gitlab-runner gitlab-runner

# we have to run as root so that we can apt-get update
ENTRYPOINT ["/data/builder.sh"]
