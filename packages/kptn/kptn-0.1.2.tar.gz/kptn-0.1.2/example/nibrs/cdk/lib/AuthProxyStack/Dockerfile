FROM --platform=linux/amd64 nginx:1.25.4-alpine3.18

COPY nginx-startup.sh /docker-entrypoint.d/40-startup.sh
COPY nginx.conf /etc/nginx/nginx.conf
RUN chmod +x /docker-entrypoint.d/40-startup.sh
