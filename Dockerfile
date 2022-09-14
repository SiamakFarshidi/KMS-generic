FROM debian:buster
RUN mkdir /var/lib/opensemanticsearch
COPY . /var/lib/opensemanticsearch
