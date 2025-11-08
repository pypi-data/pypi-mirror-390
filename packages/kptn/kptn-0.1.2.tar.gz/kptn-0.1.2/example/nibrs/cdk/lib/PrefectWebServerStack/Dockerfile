ARG PREFECT_IMAGE
FROM --platform=linux/amd64 $PREFECT_IMAGE

# Copy in the ECS work pool template
COPY ecs-work-pool-template.json /opt/prefect/
COPY scripts /opt/prefect

RUN chmod +x /opt/prefect/apply-work-pool.sh
RUN chmod +x /opt/prefect/prefect-server-entry.sh

CMD /opt/prefect/prefect-server-entry.sh