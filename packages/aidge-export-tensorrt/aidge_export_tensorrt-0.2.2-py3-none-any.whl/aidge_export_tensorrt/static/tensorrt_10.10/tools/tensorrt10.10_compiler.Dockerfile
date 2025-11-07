FROM nvcr.io/nvidia/tensorrt:25.05-py3


# Start bash login shell
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash", "-i"]
