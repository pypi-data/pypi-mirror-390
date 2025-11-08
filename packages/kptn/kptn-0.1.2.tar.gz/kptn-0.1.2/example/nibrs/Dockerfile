# This Docker image should include installations of both R and Python. Because R
# seems harder to set up ourselves, we'll start from an R base image and install
# Python into it.

FROM --platform=linux/amd64 rocker/tidyverse:4.4.0

RUN rm -rf /var/lib/apt/lists/* \
    \
    # The 99fixbadproxy file fixes an intermittent "hash sums mismatch" error when
    # downloading the packages. We don't fully understand the problem, but it appears
    # to be related to our proxy's caching behavior.
    && echo 'Acquire::http::Pipeline-Depth 0;\n \
             Acquire::http::No-Cache true;\n \
             Acquire::BrokenProxy true;' > /etc/apt/apt.conf.d/99fixbadproxy \
    && apt-get update \
    # software-properties-common provides add-apt-repository, so it needs to be
    # installed here and not with the rest of the packages below.
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    libgsl0-dev \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    libcairo2-dev \
    libxt-dev \
    cmake pandoc \
    libjemalloc2 \
    time \
    \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY ./lib/ ./lib/
ENV R_LIBS_USER=/usr/local/lib/R/site-library/
RUN R -e 'remotes::install_version("pak", "0.7.2", repos="https://packagemanager.posit.co/cran/__linux__/jammy/2024-05-20")'
RUN R -e 'options(repos = "https://packagemanager.posit.co/cran/__linux__/jammy/2024-05-20"); \
pak::pkg_install(c( \
    "./lib/ReGenesees_2.2.tar.gz", \
    "arsenal@3.6.3", \
    "Cairo@1.6-2", \
    "copula@1.1-3", \
    "DescTools@0.99.54", \
    "factoextra@1.0.7", \
    "formattable@0.2.1", \
    "fpc@2.2-12", \
    "gtools@3.9.5", \
    "here@1.0.1", \
    "Hmisc@5.1-2", \
    "logger@0.3.0", \
    "miceadds@3.17-44", \
    "moments@0.14.1", \
    "naniar@1.0.0", \
    "openxlsx@4.2.5.2", \
    "party@1.3-15", \
    "partykit@1.2-20", \
    "pspline@1.0-19", \
    "R.utils@2.12.3", \
    "rjson@0.2.21", \
    "sampling@2.10", \
    "sas7bdat@0.7", \
    "sjmisc@2.8.10", \
    "srvyr@1.2.0", \
    "stabledist@0.7-1", \
    "StatMatch@1.4.2", \
    "VIM@6.2.2", \
    "writexl@1.5.0" \
))'

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PATH=$PATH:/code/.venv/bin
ENV PYTHONPATH="/code"
COPY uv.lock pyproject.toml ./

###############################################################################
# NOTE: This command installs the packages defined in the **uv.lock** file. If you
# edit pyproject.toml, you will need to run `uv lock` or `uv sync` to update the lock file.
###############################################################################
RUN uv sync --frozen

ARG GIT_BRANCH
ARG GIT_HASH
ENV GIT_BRANCH=${GIT_BRANCH}
ENV GIT_HASH=${GIT_HASH}

COPY ./ ./

# Copy kptn package
COPY kptn-0.1.0-py3-none-any.whl /app/
RUN uv add /app/kptn-0.1.0-py3-none-any.whl
COPY kptn.yaml run.py ./

# Default command (can be overridden)
CMD [".venv/bin/python", "run.py"]