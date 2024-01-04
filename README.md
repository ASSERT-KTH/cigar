# CigaR: Cost-efficient Program Repair with LLMs

CigaR is an LLM-based APR tool that focuses on token cost minimization.



### Install CigaR dependencies

Use the install.sh script to install the dependencies:
```
git clone git@github.com:ASSERT-KTH/cigar.git
cd cigar
bash install.sh
```

This also sets the user_params.py which defines the paths to the dependencies.

The prog_params.py contains the default parameters for the analysis.


### Reproduce CigaR Analysis on Defects4J

To reproduce the results of the analysis run the following command:

```
bash run_analysis.sh
```
