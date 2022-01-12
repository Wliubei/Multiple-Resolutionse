#Urbansound8k
The generalization ability of the proposed multi-resolution approach is also evaluated on urbansound8k. The backend classifier is SENet. The results are shown in Table 1.
|    | Resolution(window/shift) | Accuracy（%）| Learned Weights | 
| :------: | :-----: | :------: | :-------: | 
|     | 512 / 64 | 61.77 | 0.98 |      
|  | 512 /128 | 69.83 | 0.23 |       
|  | 1024 / 64 | 69.35| 0.91 |       
|  |1024 /128 |71.75  | 0 |      
| Hand Selected Resolution | 1024 /256 | 77.64  | 0.01 |  
|  | 2048 / 64 | 72.11 | 0.99 |     
|  | 2048 /128 | 73.43 | 0.01 |     
|  | 2048 /256 | 72.95 | 0.03 |    
|  | 2048 /512 | 72.59  | 0.22 |        
|  | Top-3 | 72.95  |   |    
| Proposed | Full | 71.03  |   |   
|    | Refined | 79.12 |   | 
