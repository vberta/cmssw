# RDFprocessor
RDF based mini-framework

## how to get this repository

```
git clone https://github.com/emanca/RDFprocessor.git RDFprocessor
cd RDFprocessor
git checkout origin/wmass
```
## source root 6.16

`. /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh`

## how to run control plots

```
cd wmass/controlPlots
python defs.py
```

file `defs.py` calls the framework and defines the cuts to apply to the various samples and the list of variables to plot.
The dictionary structure must be preserved for the code to work.
