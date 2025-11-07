# Cardiovascular Risk Scores for the ACRIBiS Project

## Risk scores

### CHA<sub>2</sub>DS<sub>2</sub>-VASc

_(**C**ongestive heart failure/Left ventricular dysfunction, **H**ypertension, **A**ge ≥ 75 years, **D**iabetes mellitus,
Prior **S**troke/Transient ischaemic attack/Thromboembolism, **V**ascular disease, **A**ge 65-74 years, **S**ex **c**ategory)_

Original publication: https://doi.org/10.1378/chest.09-1584

Predicts the 1-year risk of thromboembolic events in patients with atrial fibrillation (AF)

### HAS-BLED

_(**H**ypertension, **A**bnormal renal and liver function, **S**troke, **B**leeding,
**L**abile international normalized ratios, **E**lderly, **D**rugs or alcohol)_

Original publication: https://doi.org/10.1378/chest.10-0134

Predicts the 1-year risk of major bleeding in AF patients

### ABC-AF

_(**A**ge, **B**iomarker, **C**linical history)_

**Stroke**

Original publication: https://doi.org/10.1093/eurheartj/ehw054
<br/>
Recalibration: https://doi.org/10.1161/CIRCULATIONAHA.120.053100

Predicts the 1-year risk of stroke in AF patients

**Bleeding**

Original publication: https://doi.org/10.1016/S0140-6736(16)00741-8
<br/>
Recalibration: https://doi.org/10.1161/CIRCULATIONAHA.120.053100

Predicts the 1-year risk of bleeding in AF patients

**Death**

Original publication: https://doi.org/10.1093/eurheartj/ehx584

Predicts the 1-year risk of death in AF patients

### CHARGE-AF

_(**C**ohorts for **H**eart and **A**ging **R**esearch in **G**enomic **E**pidemiology)_

Original publication: https://doi.org/10.1161/JAHA.112.000102

Predicts the 5-year incidence of AF

### SMART

_(**S**econdary **M**anifestations of **ART**erial disease)_

Original publication: https://doi.org/10.1136/heartjnl-2013-303640

Recalibration: https://doi.org/10.1161/CIRCULATIONAHA.116.021314

Assumptions on the effects of antithrombotic treatment: https://doi.org/10.1016/S0140-6736(09)60503-1

Predicts the 10-year risk of recurrent ischaemic events in patients with pre-existing vascular disease 

### SMART-REACH

_(**S**econdary **M**anifestations of **ART**erial disease-**RE**duction of **A**therothrombosis for **C**ontinued **H**ealth)_

Original publication: https://doi.org/10.1161/JAHA.118.009217

Predicts the 10-year risk and lifetime risk (i.e. risk until age 90 years) for (recurrent) myocardial infarction,
stroke or vascular death and (recurrent) event free life-expectancy

### MAGGIC

_(**M**eta-**A**nalysis **G**lobal **G**roup **I**n **C**hronic Heart Failure )_

Original publication: https://doi.org/10.1093/eurheartj/ehs337

> [!IMPORTANT]
> The implementation differs from the formula presented in the article!
> 
> **Statement on the website of the online calculator:**
> <br>
> From 18 September 2013, the integer score will increase by 2 if heart failure was diagnosed > 18 months ago.
> This may affect a comparison of the current result to risk assessments before this date.

Calculator returns integer risk score, can be used to look up 1- and 3-year risk of death for patients with heart failure (HF) 

### Barcelona Bio-HF

Original publication (v1): https://doi.org/10.1371/journal.pone.0085466

Recalibration (v2): https://doi.org/10.1002/ejhf.949

Recalibration (v3): https://doi.org/10.1002/ejhf.2752

Predicts risk of all-cause death, HF-related hospital readmission, the combination of both endpoints, and life expectancy

Predicts the risk at 1 to 5 years 

## Publication

Preliminary results presented at GMDS Jahrestagung 2024: https://doi.org/10.3205/24GMDS112

## Installation

### Using pip

```Python
pip install acribis-scores
```

### From source

```Shell
# Clone repository
git clone git@github.com:IMI-HD/acribis_scores_python.git
cd acribis_scores_python
```

**Windows**
```Shell
# Build
py -m build

# Install
py -m pip install dist/acribis_scores-<version>-py3-none-any.whl

# Run simple gui
py src/demo/gui.py
```

**Linux**
```Shell
# Build
python3 -m build

# Install
python3 -m pip install dist/acribis_scores-<version>-py3-none-any.whl

# Run simple gui
python3 src/demo/gui.py
```

### Testing
For automated testing against the R implementation and online/Excel calculators (if available) of these scores,
clone the R project and follow the instructions there (https://github.com/IMI-HD/acribis_scores_r).
Run the R Shiny app locally on port 80 and keep it running while executing the tests:

```Shell
# In the acribis_scores_r folder
shiny::runApp("app/demo_gui.R", port=80)
```

Install the package with additional optional dependencies and run the tests:

```Shell
# Install with optional test dependencies
pip install acribis-scores[test]
```

**Windows**
```Shell
# In the acribis_scores_python folder
py -m unittest discover tests
```

**Linux**
```Shell
# In the acribis_scores_python folder
python3 -m unittest discover tests
```