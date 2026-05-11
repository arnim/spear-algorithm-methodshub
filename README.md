# SPEAR: Ranking User Expertise and Resource Quality from Time-Ordered Interactions

[![Launch with Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/arnim/spear-algorithm-methodshub/HEAD?urlpath=lab/tree/spear_algorithm.ipynb)
[![Launch with Jupyter4NFDI](https://img.shields.io/badge/Launch-Jupyter4NFDI-orange)](https://hub.nfdi-jupyter.de/v2/gh/arnim/spear-algorithm-methodshub/HEAD?urlpath=lab/tree/spear_algorithm.ipynb&localstoragepath=%2Fhome%2Fjovyan%2Fwork)

Open the notebook directly in a temporary executable environment with [mybinder.org](https://mybinder.org/) or [Jupyter4NFDI](https://nfdi-jupyter.de/users/jupyterlab/repo2docker).

## Description

SPEAR estimates which users are likely to be experts and which resources are likely to be high quality from a chronological list of user-resource interactions. It is useful when the timing of an interaction matters: users who discover resources before other users do can receive more credit than later users. The method returns two ranked tables, one for user expertise and one for resource quality.

SPEAR takes tabular activity data as input. Each row should identify a timestamp, a user, and a resource. The implementation in [`spear.py`](spear.py) first creates a weighted user-resource matrix and then iteratively updates user expertise and resource quality scores. The accompanying notebook [`spear_algorithm.ipynb`](spear_algorithm.ipynb) demonstrates the complete workflow on a small public example dataset.

The algorithm follows Noll et al. (2009), who introduced SPEAR for telling experts from spammers in social bookmarking and folksonomy data. It is related to Kleinberg's (1999) HITS algorithm, but adds time-aware credit scoring for early user-resource interactions. This repository uses a small synthetic dataset in [`data/social_bookmarks.csv`](data/social_bookmarks.csv), so all examples are reproducible without credentials or external data access. The Python implementation was checked against the public project documentation (Noll, n.d.) and the Julia implementation by Bleier (2013).

Important parameters are the credit scoring function and the number of iterations. The default `sqrt_credit` function gives earlier users more credit while dampening very large differences. The `constant_credit` option ignores timing and can be used as a robustness comparison similar to a HITS-style ranking.

## Use Cases

- Identifying knowledgeable curators in social bookmarking data. One can use SPEAR to rank users who repeatedly find resources that later become popular among other users.
- Ranking resources in online communities. One can use SPEAR to prioritize links, posts, documents, or datasets that are connected to high-expertise users.
- Comparing expert and spam-like behavior. One can inspect whether accounts that mostly promote low-quality or isolated resources receive low expertise scores.
- Studying early adoption in digital behavioral data. One can apply SPEAR to timestamped interactions such as bookmarks, likes, citations, reposts, or hyperlink creation.

Example publication:

- Noll, M. G., Au Yeung, C.-m., Gibbins, N., Meinel, C., & Shadbolt, N. (2009). Telling experts from spammers. In *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval* (pp. 612–619). https://doi.org/10.1145/1571941.1572046

## Input Data

SPEAR takes a CSV table with one interaction per row. The example input file is [`data/social_bookmarks.csv`](data/social_bookmarks.csv):

```csv
timestamp,user,resource,tag
2026-01-01 09:00,Alice,open-data-portal,data
2026-01-01 09:05,Bob,open-data-portal,statistics
2026-01-01 09:10,Chandra,miracle-cure-shop,health
```

Required fields:

- `timestamp`. Time at which the activity happened. This field is required because SPEAR uses chronological order.
- `user`. Actor identifier, such as an account, author, or participant ID. Required.
- `resource`. Item identifier, such as a URL, document, post, paper, or dataset. Required.

Optional fields such as `tag` can be present but are ignored by the basic implementation.

## Output Data

The method returns three pandas data frames:

- `expertise`: users ranked by normalized expertise score;
- `quality`: resources ranked by normalized quality score;
- `adjacency`: the weighted user-resource matrix used by the algorithm.

Example output shape:

| user | expertise |
| --- | ---: |
| Alice | 0.31 |
| Bob | 0.28 |

| resource | quality |
| --- | ---: |
| open-data-portal | 0.37 |
| validated-election-data | 0.34 |

Scores are relative within the analyzed dataset and sum to one.

## Hardware Requirements

The example notebook runs on standard Binder hardware with one CPU and less than 1 GB of memory. Larger datasets may require more memory because the simple implementation stores the user-resource matrix in memory.

## Environment Setup

Install Python 3.10 or newer and the packages in [`requirements.txt`](requirements.txt):

```bash
pip install -r requirements.txt
```

Binder also uses [`postBuild`](postBuild) to install Quarto support for Methods Hub rendering.

## How to Use

Open and run [`spear_algorithm.ipynb`](spear_algorithm.ipynb) in JupyterLab, or execute the method from Python:

```python
import pandas as pd
from spear import run_spear, sqrt_credit

activities = pd.read_csv("data/social_bookmarks.csv", parse_dates=["timestamp"])
result = run_spear(activities, credit=sqrt_credit, iterations=20)

print(result.expertise)
print(result.quality)
```

To compare with a non-temporal baseline, replace `sqrt_credit` with `constant_credit`.

## Example Commands and Parameters

Run the notebook locally:

```bash
jupyter nbconvert --to notebook --execute spear_algorithm.ipynb --output /tmp/spear_algorithm_executed.ipynb
```

Test the Binder build locally with repo2docker:

```bash
repo2docker --no-run .
```

Main parameters in [`spear.py`](spear.py):

- `credit`: credit scoring function. Use `sqrt_credit` for time-aware SPEAR or `constant_credit` for a non-temporal comparison.
- `iterations`: maximum number of expertise/quality update steps.
- `tolerance`: convergence threshold.
- `user_col`, `resource_col`, `time_col`: input column names.

## AI Use Acknowledgement

This submission was prepared with assistance from an AI coding assistant. The assistant helped draft explanatory text, create the example notebook structure, implement and test the Python code, and check Binder readiness. The author reviewed, edited, and takes responsibility for the final content, code, and citations.

## References

The references follow a consistent APA style, in line with the Methods Hub guidelines.

- Bleier, A. (2013). *SpearAlgorithm.jl* [Computer software]. GitHub. Retrieved May 11, 2026, from https://github.com/arnim/SpearAlgorithm.jl
- Kleinberg, J. M. (1999). Authoritative sources in a hyperlinked environment. *Journal of the ACM, 46*(5), 604–632. https://doi.org/10.1145/324133.324140
- Noll, M. G. (n.d.). *SPEAR algorithm*. Retrieved May 11, 2026, from https://www.michael-noll.com/projects/spear-algorithm/
- Noll, M. G., Au Yeung, C.-m., Gibbins, N., Meinel, C., & Shadbolt, N. (2009). Telling experts from spammers. In *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval* (pp. 612–619). Association for Computing Machinery. https://doi.org/10.1145/1571941.1572046

## Contact Details

For questions about this Methods Hub submission, contact Arnim Bleier via the repository issue tracker.

## Funding Acknowledgement

This work was supported by Jupyter4NFDI, funded through Base4NFDI by the German Research Foundation (DFG), project number 521453681.
