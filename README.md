Ssurgo PROVIDER
==============

By using this code you are able to retrieve soil composition for severals point over the USA.
For more information see https://www.nrcs.usda.gov/wps/portal/nrcs/detail/soils/survey/?cid=nrcs142p2_053627

1. Requirements

Download data from https://gdg.sc.egov.usda.gov/GDGOrder.aspx and unzip it.

2. How to use it

a. With Conda
-------------
Create conda environement: 
> conda create -n ssurgo_provider python=3.8

> conda activate ssurgo_provider

> conda install --file requirements.txt

Call retrieve_soil_composition (from src.main) with list of fields coordinates [ (lat_0, long_0), (lat_1, long_1), ...]
and the path where the Ssurgo geodatabase is uncompress.

See example in example/retrieve_soil_data

b. With Docker

0. prepare folder with state gdb
On your computer, create a folder named SSURGO and put alle the gdb state file inside

1. build image in the project
> docker build . -t ssurgo_linux_docker:0.0.1 -f .\docker\Dockerfile

2. launch the container
> docker run --mount type=bind,source=<folder path define in step 0>,target=/resources  -p 8180:8180 ssurgo_linux_docker:0.0.1

> docker run --mount type=bind,source=C://work//ssurgo_provider//resources//SSURGO,target=/resources/SSURGO  -p 8180:8180 ssurgo_linux_docker:0.0.1