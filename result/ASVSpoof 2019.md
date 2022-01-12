#ASVSpoof 2019
In this section, we consider 3 window lengths (512, 1024, and 2048) and 4 frame shifts (64, 128, 256, and 512) and their combinations as listed in Table 1. Four special choices are also included from literatures, i.e., 400/160 from [1], 1724/130 from [2], 288/96 and 480/120 from [3].
The results on ASVSpoof 2019 are reported in Table 1.
|    | Resolution(window/shift) | LA EER(Eval)| PA EER(Eval) | 
| :------: | :-----: | :------: | :-------: | 
|     | 512 / 64 | 14.14 | 33.08 |      
|  | 512 /128 | 36.03 | 36.17 |       
|  | 1024 / 64 | 38.60 | 37.32 |       
|  |1024 /128 | 6.86  | 27.60 |      
|  | 1024 /256 | **3.53**  | 25.55 |  
|  | 2048 / 64 | 13.44 | 28.50 |     
|  | 2048 /128 | 40.45 | 37.98 |     
| Hand Selected Resolution | 2048 /256 | 42.04 | 39.59 |    
|  | 2048 /512 | 7.61  | 27.49 |    
|  | 400 /160 | 4.82  | 20.30 |    
|  | 1724 /130 | 7.15  | 19.99 |    
|  | 288 / 96 | 4.99  | 18.05 |     
|  | 480 /120 | 6.63  | 18.58 |     
|  | Top-3 | 5.06  | 18.32 |    
| Proposed | Full | 6.64  | 18.58 |   
|    | Refined | 7.56  | 18.07 |   
[1] Cheng-I Lai, Nanxin Chen, Jesus Villalba, and Najim De- ´ hak, “ASSERT: Anti-Spoofing with Squeeze-Excitation and Residual Networks,” in 2019, ISCA, 2019, pp. 1013–1017
[2] Galina Lavrentyeva, Sergey Novoselov, Andzhukaev Tseren, Marina Volkova, Artem Gorlanov, and Alexandr Kozlov, “STC Antispooﬁng Systems for the ASVspoof2019 Challenge,” in Proc. Interspeech,2019, pp. 1033–1037
[3] Wang, Q.; Lee, K.A.; Koshinaka, T. “Using multi-resolution feature maps with convolutional neural networks for anti-spooﬁng in ASV,” in Proceedings of the Odyssey Speaker and Language Recognition Workshop,Tokyo, Japan, 1–5 November 2020; pp. 138–142.
#Statistical Significance
We have run the experiments on ASVSpoof 2019 LA for 5 times. The results are given in Table 2.
| Experiment ID | Refined| 1724/130 | 
| :------: | :-----: | :------: |
| 1 | 3.92 | 6.59 |
| 2 | 3.38 | 6.06 |
| 3 | 3.80 | 3.72 |
| 4 | 3.36 | 3.53 |
| 5 | 3.90 | 7.03 |
| mean | 3.67 | 5.38 |
| standard deviation | 0.249 | 1.469 |
