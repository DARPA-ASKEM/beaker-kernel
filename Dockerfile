FROM python:3.10
RUN useradd -m jupyter
EXPOSE 8888

# Install Julia
 RUN wget --no-verbose -O julia.tar.gz "https://julialang-s3.julialang.org/bin/linux/$(uname -m|sed 's/86_//')/1.9/julia-1.9.0-linux-$(uname -m).tar.gz"
 RUN tar -xzf "julia.tar.gz" && mv julia-1.9.0 /opt/julia && \
     ln -s /opt/julia/bin/julia /usr/local/bin/julia && rm "julia.tar.gz"

COPY environments/julia /home/jupyter/.julia/environments/v1.9
RUN chown -R jupyter:jupyter /home/jupyter
RUN chmod -R 755 /home/jupyter/.julia
USER jupyter
RUN julia -e 'using Pkg; Pkg.instantiate(); Pkg.build("IJulia")'
USER root

WORKDIR /jupyter
# Install Python requirements
RUN pip install jupyterlab jupyterlab_server pandas matplotlib xarray numpy poetry scipy

# Install project requirements
COPY --chown=1000:1000 pyproject.toml poetry.lock /jupyter/
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Install Mira from `hackathon` branch
RUN git clone https://github.com/indralab/mira.git /mira
WORKDIR /mira
RUN git checkout hackathon
RUN python -m pip install -e .
RUN apt-get update && \
    apt-get install -y graphviz libgraphviz-dev
RUN python -m pip install -e ."[ode,tests,dkg-client,sbml]"
WORKDIR /jupyter

# Kernel hast to go in a specific spot
COPY llmkernel /usr/local/share/jupyter/kernels/llmkernel

# Copy src code over
RUN chown 1000:1000 /jupyter
COPY --chown=1000:1000 . /jupyter

# Switch to non-root user
USER 1000

CMD ["python", "main.py", "--ip", "0.0.0.0"]

