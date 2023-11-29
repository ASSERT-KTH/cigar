# Conversational Automated Program Repair

CigaR is an APR tool based on the idea of 
[ChatRepair](https://arxiv.org/abs/2304.00385). The current repository was created as part of a [Master Thesis](https://www.overleaf.com/read/jqdghfrwhhkc) and contains the implementation and benchmark results of ChatRepair and RapidCapr on 6 projects of the Defects4J dataset.



### Install RapidCapr dependencies

Use the install.sh script to install the dependencies:
```
git clone git@github.com:ASSERT-KTH/RapidCapr.git
cd RapidCapr
bash install.sh
```

This also sets the user_params.py which defines the paths to the dependencies.

The prog_params.py contains the default parameters for the analysis.


### Reproduce RapidCapr Analysis on Defects4J

To reproduce the results of the analysis run the following command:

```
bash run_analysis.sh
```
