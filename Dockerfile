FROM ghcr.io/darpa-askem/askem-julia:5.0.0 AS JULIA_BASE_IMAGE

FROM python:3.10

USER root

# Install custom Julia
ENV JULIA_PATH=/usr/local/julia
ENV JULIA_DEPOT_PATH=/usr/local/julia
ENV JULIA_PROJECT=/home/jupyter/.julia/environments/askem

COPY --chown=1000:1000 --from=JULIA_BASE_IMAGE /usr/local/julia /usr/local/julia
COPY --chown=1000:1000 --from=JULIA_BASE_IMAGE /Project.toml /Manifest.toml /home/jupyter/.julia/environments/askem/
RUN chmod -R 777 /usr/local/julia/logs
RUN ln -sf /usr/local/julia/bin/julia /usr/local/bin/julia

# Install r-lang and kernel
RUN apt update && \
    apt install -y r-base r-cran-irkernel \
        graphviz libgraphviz-dev \
        libevent-core-2.1-7 libevent-pthreads-2.1-7 && \
    apt clean -y && \
    apt autoclean -y

# Switch to non-root user. It is crucial for security reasons to not run jupyter as root user!
RUN useradd -m jupyter
USER jupyter

# Install Mira from github
RUN git clone https://github.com/indralab/mira.git /home/jupyter/mira && \
    pip install --no-cache-dir /home/jupyter/mira/"[ode,tests,dkg-client,sbml]" && \
    rm -r /home/jupyter/mira

# Install project requirements
COPY --chown=1000:1000 pyproject.toml README.md hatch_build.py /home/jupyter/askem_beaker/
RUN mkdir -p /home/jupyter/askem_beaker/src/askem_beaker && touch /home/jupyter/askem_beaker/src/askem_beaker/__init__.py
RUN pip install --no-cache-dir --upgrade -e /home/jupyter/askem_beaker

COPY --chown=1000:1000 . /home/jupyter/askem_beaker/

# Installs the askem specific subkernels
RUN pip install --no-cache-dir --upgrade /home/jupyter/askem_beaker

#WORKDIR /askem_beaker
WORKDIR /home/jupyter


# Install Julia kernel (as user jupyter)
RUN /usr/local/julia/bin/julia -e 'using IJulia; IJulia.installkernel("julia"; julia=`/usr/local/julia/bin/julia --threads=4`)'

CMD ["python", "-m", "beaker_kernel.server.main", "--ip", "0.0.0.0"]
