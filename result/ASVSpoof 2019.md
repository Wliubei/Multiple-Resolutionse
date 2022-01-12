###ASVSpoof 2019

In this section, we consider 3 window lengths (512, 1024, and 2048) and 4 frame shifts (64, 128, 256, and 512) and their combinations as listed in Table 1. Four special choices are also included from literatures, i.e., 400/160 from [1], 1724/130 from [2], 288/96 and 480/120 from [3].
The results on ASVSpoof 2019 are reported in Table 1.
|    | Resolution(window/shift) | LA EER(Eval)| PA EER(Eval) | 
| :------: | :-----: | :------: | :-------: | 
|     | 512 / 64 | 10.60 | 4.06 |      
|  | 512 /128 | 11.56 | 3.40 |       
|  | 1024 / 64 | 16.72 | 2.89 |       
|  |1024 /128 | 8.15  |2.33 |      
|  | 1024 /256 | 11.72  | 2.76 |  
|  | 2048 / 64 | 5.72 | 1.79 |     
|  | 2048 /128 | 9.88 | 2.20 |     
| Hand Selected Resolution | 2048 /256 | 4.67 | 2.53 |    
|  | 2048 /512 | 5.54  | 2.69 |    
|  | 400 /160 | 9.24  | 3.75 |    
|  | 1724 /130 | 5.38  | 2.10 |    
|  | 288 / 96 |    | 3.91 |     
|  | 480 /120 |    | 3.09 |     
|  | Top-3 | 10.21  | 2.66 |    
| Proposed | Full | 5.43  | 1.07 |   
|    | Refined | 3.67  | 1.24 |   
> 
[1] Cheng-I Lai, Nanxin Chen, Jesus Villalba, and Najim De- ´ hak, “ASSERT: Anti-Spoofing with Squeeze-Excitation and Residual Networks,” in 2019, ISCA, 2019, pp. 1013–1017
[2] Galina Lavrentyeva, Sergey Novoselov, Andzhukaev Tseren, Marina Volkova, Artem Gorlanov, and Alexandr Kozlov, “STC Antispooﬁng Systems for the ASVspoof2019 Challenge,” in Proc. Interspeech,2019, pp. 1033–1037
[3] Wang, Q.; Lee, K.A.; Koshinaka, T. “Using multi-resolution feature maps with convolutional neural networks for anti-spooﬁng in ASV,” in Proceedings of the Odyssey Speaker and Language Recognition Workshop,Tokyo, Japan, 1–5 November 2020; pp. 138–142.

###Statistical Significance

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
