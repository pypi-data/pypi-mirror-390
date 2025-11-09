FROM docker.io/library/python:3.11 as builder

WORKDIR /tmp

COPY . .
RUN pip install --no-cache-dir -U "build>=1.0.3" &&\
	python -m build .

FROM docker.io/library/python:3.11-alpine as runtime

ARG UID=3000
ARG GID=3000
RUN addgroup -g ${GID} certbot &&\
  adduser \
    -h /var/lib/certbot \
    -k /dev/null \
    -s /sbin/nologin \
    -u ${UID} \
    -g certbot \
    -D \
    -S \
    certbot 

COPY --from=builder  /tmp/dist/ /tmp/dist

ARG UID=3000
ARG GID=3000
RUN pip install --no-cache-dir "certbot>=2.7.1" /tmp/dist/*.whl &&\
	rm -rf /tmp/dist &&\
	mkdir -p /var/log/letsencrypt /var/lib/letsencrypt /etc/letsencrypt &&\
	chown -R "${UID}:${GID}" /var/log/letsencrypt /var/lib/letsencrypt /etc/letsencrypt

ARG UID=3000
USER $UID

ENTRYPOINT ["/usr/local/bin/certbot", "--authenticator=dns-leaseweb", "--dns-leaseweb-credentials=/etc/letsencrypt/credentials/leaseweb.ini"]
CMD []
