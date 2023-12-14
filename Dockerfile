#FROM ghcr.io/darpa-askem/askem-julia:latest AS JULIA_BASE_IMAGE


FROM python:3.10
RUN useradd -m jupyter
EXPOSE 8888

RUN mkdir -p /usr/local/share/jupyter/kernels && chmod -R 777 /usr/local/share/jupyter/kernels


# Install r-lang and kernel
RUN apt update && \
    apt install -y r-base r-cran-irkernel \
        graphviz libgraphviz-dev && \
    apt clean -y && \
    apt autoclean -y

WORKDIR /jupyter

# Install Python requirements
RUN pip install --upgrade --no-cache-dir hatch pip

# Install project requirements
COPY --chown=1000:1000 pyproject.toml README.md hatch_build.py /jupyter/
# Hack to install requirements without requiring the rest of the files
RUN pip install -e .

# Kernel must be placed in a specific spot in the filesystem
# TODO: Replace this with helper that just copies the required file(s) via a python script?
COPY beaker_kernel/kernel.json /usr/local/share/jupyter/kernels/beaker_kernel/kernel.json

# Copy src code over
COPY --chown=1000:1000 . /jupyter
RUN chown -R 1000:1000 /jupyter
RUN pip install .

# Switch to non-root user. It is crucial for security reasons to not run jupyter as root user!
USER jupyter

# Service
CMD ["python", "/jupyter/service/main.py", "--ip", "0.0.0.0"]
