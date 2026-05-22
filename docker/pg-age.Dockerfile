FROM pgvector/pgvector:pg17

RUN apt-get update && apt-get install -y \
    build-essential \
    libreadline-dev \
    zlib1g-dev \
    flex \
    bison \
    git \
    postgresql-server-dev-17 \
    && git clone --depth 1 --branch PG17 https://github.com/apache/age.git /tmp/age \
    && cd /tmp/age \
    && make install PG_CONFIG=/usr/bin/pg_config \
    && cd / \
    && rm -rf /tmp/age \
    && apt-get purge -y build-essential libreadline-dev zlib1g-dev flex bison git postgresql-server-dev-17 \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
