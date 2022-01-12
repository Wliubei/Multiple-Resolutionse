###ASVSpoof 2017
The generalization ability of the proposed multi-resolution approach is also evaluated on ASVSpoof 2017. The backend classifier is LCNN from [4]. The results are reported in Table 1
|    | Resolution(window/shift) | EER (Eval Set, in%)| Weights | 
| :------: | :-----: | :------: | :-------: | 
|     | 512 / 64 | 21.71 | 0 |      
|  | 512 /128 | 20.45 | 0 |       
|  | 1024 / 64 | 23.06 | 0.98 |       
|  |1024 /128 | 22.23  | 0 |      
|  | 1024 /256 | 22.46  | 0.1 |  
|  | 2048 / 64 | 23.24 | 0.95 |     
|  | 2048 /128 | 22.58 | 0 |     
| Hand Selected Resolution | 2048 /256 | 22.89 | 0 |    
|  | 2048 /512 | 21.89  | 0 |    
|  | 400 /160 | 9.24  | 3.75 |    
|  | 1724 /130 | 5.38  | 2.10 |    
|  | 288 / 96 | 22.04 | 0 |     
|  | 480 /120 |  21.69  | 0.99 |     
|  | Top-3 | 10.21  | 2.66 |    
| Proposed | Full | 5.43  | 1.07 |   
|    | Refined | 3.67  | 1.24 | 
