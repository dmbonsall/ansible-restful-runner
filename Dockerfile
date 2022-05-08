FROM alpine:latest

# Install packages
RUN apk add --no-cache python3 python3-dev build-base libffi-dev openssh-client rsync && \
    python3 -m ensurepip && \
    python3 -m pip install -U pip setuptools wheel && \

    # Create directories
    mkdir -p /restful_runner/etc /restful_runner/restful_runner && \
    mkdir -p /ansible/project /ansible/inventory /ansible/env /ansible/artifacts && \

    # Enable ssh to use rsa keys
    echo "PubkeyAcceptedKeyTypes +ssh-rsa" >> /etc/ssh/ssh_config

# Install the python deps (this can take a while....)
COPY requirements.txt /restful_runner/etc/requirements.txt
RUN python3 -m pip install -r /restful_runner/etc/requirements.txt && \
    apk del --no-cache build-base libffi-dev

# Copy all the other files into the image
COPY restful_runner/ /restful_runner/restful_runner
COPY logging.json /restful_runner/etc/logging.json

# Setup the execution environment
WORKDIR /restful_runner

ENV PYTHONPATH="/restful_runner" \
    API_HOST="0.0.0.0" \
    API_PORT="8123"

EXPOSE 8123/tcp

CMD uvicorn --host ${API_HOST} \
            --port ${API_PORT} \
            --log-config /restful_runner/etc/logging.json \
            restful_runner.api:app
