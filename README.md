# A MULTI-RESOLUTION FRONT-END FOR END-TO-END SPEECH ANTI-SPOOFING
### Getting started
`requirements.txt` must be installed for execution. We state our experiment environment for those who prefer to simulate as similar as possible. 
- Installing dependencies
```
pip install -r requirements.txt
```
### Data preparation
We train/validate/evaluate Multiple-Resolutions using the ASVspoof 2019  dataset.
(Alternative) Manual preparation is available via 
- ASVspoof2019 dataset: https://datashare.ed.ac.uk/handle/10283/3336
### Trainning and evaluation
In the configuration file, you can set the number of resolutions and Whether to choose the resolution.
"High_contributionn" represents the index of the resolution that has been filtered.
"Full" stands for all resolutions.
"screen" Represents whether the model filters the resolution.
- When high-weight resolutions need to be filtered, we set "screen = true" and train. After the first training, run eval.py. The resolution subdivision mechanism is automatically executed when the eval.py file is run for the first time. The index of the high resolution with the selected weight will be saved in the HighContribution.txt.
- Copy the index from HighContribution.txt to "High_contribution" in the configuration file. Set "screen = false". Train again using the optimal resolution combination. Resolution is set to the number of resolutions filtered out.

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
