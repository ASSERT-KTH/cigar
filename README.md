# CigaR: Cost-efficient Program Repair with LLMs

CigaR is an LLM-based APR tool that focuses on token cost minimization. See [CigaR: Cost-efficient Program Repair with LLMs](http://arxiv.org/pdf/2402.06598) (2024).

The paper to cite is 

```bibtex
@techreport{cigar2402.06598,
 title = {CigaR: Cost-efficient Program Repair with LLMs},
 year = {2024},
 author = {Dávid Hidvégi and Khashayar Etemadi and Sofia Bobadilla and Martin Monperrus},
 url = {http://arxiv.org/pdf/2402.06598},
 number = {2402.06598},
 institution = {arXiv},
}
```

## Repairing Defects4J Bugs

To fix Defects4J bugs, you should be using Java 8 and have installed `libdbi-perl`.

### Install CigaR dependencies

Use the install.sh script to install the dependencies:
```
git clone git@github.com:ASSERT-KTH/cigar.git
cd cigar
bash install.sh
```

This also sets the user_params.py which defines the paths to the dependencies.

You must set three params in user.params.py: `JAVA_HOME`, `TMP_DIR`, and `API_KEY`. `JAVA_HOME` should refer to the home directory of Java 8 on your machine.

The prog_params.py contains the default parameters for the analysis.

### Fixing a Single Defects4J Bug

To repair a Defects4J bug, run the following:
```
./cigar.sh {project-id} {bug-id}
```
For example, you can run:
```
./cigar.sh Chart 1
```

The resulting plausible patches are stored in `output/defects4j_CigaR/plausible_patches/`.

### Reproduce CigaR Analysis on Defects4J

To reproduce the results of the analysis, first set the `cigar_max_sample_count=100 and cigar_max_mpps_try_per_mode=5` in prog_params.py. Then, run the following command:

```
bash run_analysis.sh
```
