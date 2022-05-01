FROM continuumio/miniconda3
ENV LANG C.UTF-8

ADD ./ /src/

SHELL ["/bin/bash", "-c"]


# Create a wheel of my project
RUN conda create -n myenv python=3.7 wheel
RUN source activate myenv && cd /src && python setup.py bdist_wheel

FROM continuumio/miniconda3
SHELL ["/bin/bash", "-c"]

COPY --from=0 /src/dist/*.whl /opt/ssurgo_provider/

RUN mkdir -p resources/gSSURGO_KS.gdb
COPY ../resources/SSURGO/gSSURGO_KS.gdb/* /resources/gSSURGO_KS.gdb/
COPY ../resources/SSURGO/gSSURGO_OH.gdb/* /resources/gSSURGO_OH.gdb/
COPY ../resources/MAP/gadm36_USA_shp/* /resources/MAP/gadm36_USA_shp/

ENV SSURGO_DATA /resources/
RUN export SSURGO_DATA

# Install wheel of my project into container
RUN conda create -n myenv python=3.7
RUN source activate myenv && conda install flask gdal pandas shapely
RUN source activate myenv &&  pip install --no-cache-dir /opt/ssurgo_provider/ssurgo_provider-0.2.0-py3-none-any.whl

# open docker port
EXPOSE 8180/tcp

# define entry point
COPY docker/app_main.py src/app_main.py
ENTRYPOINT ["/opt/conda/envs/myenv/bin/python", "src/app_main.py"]

