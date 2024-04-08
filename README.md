# CigaR: Cost-efficient Program Repair with LLMs

CigaR is an LLM-based APR tool that focuses on token cost minimization. See [CigaR: Cost-efficient Program Repair with LLMs](http://arxiv.org/pdf/2402.06598) (2024).

The paper to cite is 

```bibtex
@techreport{2402.06598,
 title = {CigaR: Cost-efficient Program Repair with LLMs},
 year = {2024},
 author = {Dávid Hidvégi and Khashayar Etemadi and Sofia Bobadilla and Martin Monperrus},
 url = {http://arxiv.org/pdf/2402.06598},
 number = {2402.06598},
 institution = {arXiv},
}
```



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
