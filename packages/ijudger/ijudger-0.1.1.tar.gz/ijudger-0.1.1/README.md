# ijudger

## Overview

ijudger is a lightweight judge system for competitive programming, designed for testing Python and C++ solutions.
It supports time and memory limits for code execution.

## Features

* Judge solutions with given test cases
* Support for Python and C++
* Generate JSON test data (`makeproblemjson` command)
* Configurable time and memory limits
* Return verdicts: AC / WA / TLE / RE / MLE

## Installation

Install via PyPI:

```
pip install ijudger
```

Or clone from GitHub:

```
git clone https://github.com/your-repo/ijudger.git
cd ijudger
pip install .
```

## Usage

### 1. Generate JSON test data

```
makeproblemjson <problem_folder> <time_limit(s)> <memory_limit(MB)> [output.json]
```

Example:

```
makeproblemjson aplusb 1 128 aplusb.json
```
