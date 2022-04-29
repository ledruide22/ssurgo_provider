FROM continuumio/miniconda3
ENV LANG C.UTF-8

ADD ./ /src/

SHELL ["/bin/bash", "-c"]


# Create a wheel of my project
RUN conda create -n myenv python=3.7 wheel
RUN source activate myenv && cd /src && python setup.py bdist_wheel

FROM continuumio/miniconda3
SHELL ["/bin/bash", "-c"]

# Install wheel of my project into container
RUN conda create -n myenv python=3.7
RUN source activate myenv && conda install flask gdal panda
RUN source activate myenv &&  pip install --no-cache-dir /opt/ssurgo_provider/ssurgo_provider-0.2.0-py3-none-any.whl

# open docker port
EXPOSE 8180/tcp

# define entry point
COPY docker/app_main.py src/app_main.py
ENTRYPOINT ["/opt/conda/envs/myenv/bin/python", "src/main.py"]

