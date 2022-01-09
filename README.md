# Multiple-Resolutionse
### Getting started
`requirements.txt` must be installed for execution. We state our experiment environment for those who prefer to simulate as similar as possible. 
- Installing dependencies
```
pip install -r requirements.txt
```
### Data preparation
We train/validate/evaluate Multiple-Resolutions using the ASVspoof 2019  dataset .
(Alternative) Manual preparation is available via 
- ASVspoof2019 dataset: https://datashare.ed.ac.uk/handle/10283/3336
To train :
```
python train.py --config _/config/config_LA_SEet34.json  --device 0
```
To evaluate 
```
python eval.py --resume beat.pth --protocol_file ASVspoof2019.PA.cm.eval.trl.txt --asv_score_file ASVspoof2019.PA.eval.asv.scores.txt
```
