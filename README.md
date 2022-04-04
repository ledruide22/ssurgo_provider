Ssurgo PROVIDER
==============

By using this code you are able to retrieve soil composition for severals point over the USA.
For more information see https://www.nrcs.usda.gov/wps/portal/nrcs/detail/soils/survey/?cid=nrcs142p2_053627

1. Requirements

Download data from https://gdg.sc.egov.usda.gov/GDGOrder.aspx or https://nrcs.app.box.com/v/soils/folder/148414960239 and unzip it.

2. How to use it

Create conda environement: 
> conda create -n ssurgo_provider python=3.8

> conda activate ssurgo_provider

> conda install --file requirements.txt

Call retrieve_soil_composition (from src.main) with list of fields coordinates [ (lat_0, long_0), (lat_1, long_1), ...]
and the path where the Ssurgo geodatabase is uncompress.

See example in example/retrieve_soil_data

