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

In the configuration file, you can set the number of resolutions and whether to filter according to the parameters of the model.
High_contributionn represents the index of the resolution that has been filtered.
"Full" stands for all resolutions.
- When no screening is performed, screen = true, training is performed.After the first training, run eval.py.The index of the high resolution with the selected weight will be saved in the HighContribution.txt.
- Copy the index in HighContribution.txt to "high_contribution" in the configuration file.screen = false.Use the optimal resolution combination to train again.Resolution is set to the number of resolutions filtered out.

```
"arch": {
        "type": "se_resnet34",
        "args": {
            "resolution": 13,
            "Full":[(128,32),(256,64), (400, 160),(512, 64), (512, 128), (1024, 64), (1024, 128), (1024, 256), (2048, 128), (2048, 256), (1724, 130),
                     (2048, 512), (2048, 64)],
            "High_contribution": [12, 10, 4, 11, 3, 7, 6],
            "screen": true
        }
    }
  ```
  To train :
```
python train.py --config _/config/config_LA_SEet34.json  --device 0
```
To evaluate 
```
python eval.py --resume beat.pth --protocol_file ASVspoof2019.PA.cm.eval.trl.txt --asv_score_file ASVspoof2019.PA.eval.asv.scores.txt
```
