# Beaker Kernel: ASKEM
This is the ASKEM beaker-kernel, it contains a set of context/tools that can work with 
- models
- model configurations
- datasets
- decapodes

Please see [Beaker Kernel](https://github.com/jataware/beaker-kernel) for instructions and guidances on how beaker works.


## Usage
- Copy `env.example` into `.env`, modify the environment variables as needed
- Run `docker-compose up`

Note currently askem-julia is not well supported on ARM-based architecture, you may need to remove the references from the Dockerfile in order to build.
