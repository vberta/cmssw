# RDFprocessor
RDF based mini-framework

## how to get this repository

```
git clone https://github.com/emanca/RDFprocessor.git RDFprocessor
cd RDFprocessor
git checkout origin/wmass
```
## source root master nightlies slc6

`source /cvmfs/sft-nightlies.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc7-opt/setup.sh`

## source root master nightlies slc7

`source /cvmfs/sft-nightlies.cern.ch/lcg/views/dev3/latest/x86_64-centos7-gcc62-opt/setup.sh`

## how to run control plots

```
cd wmass/controlPlots
python defs.py
```

file `defs.py` calls the framework and defines the cuts to apply to the various samples and the list of variables to plot.
The dictionary structure must be preserved for the code to work.
