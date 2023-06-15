FROM python:3.8.16-slim-buster

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone \
    && apt-get clean && apt-get -qq update && apt-get install -yq sudo wget vim openssh-client \
    && rm -rf /var/lib/apt/lists/*

## create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

WORKDIR /home/appuser/project/
COPY --chmod=777 ./ /home/appuser/project/

RUN pip install -r ./requirements.txt --no-cache-dir && pip cache purge

CMD ["python", "main.py"]