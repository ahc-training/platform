# spark-processes

## Git usage

> Clone the repo  
`git clone https://github.com/Adoe/training-tools.git`  

> Create a branch using the git subtree command for the folder only  
`git subtree split --prefix=demo -b demo`  

> Create a new empty github repo in gogs 
> Add this new repo as a remote  
`git remote add upstream https://gogs-svc.devops.svc/training-tools/spark-processes`  

> Push the subtree  
`git push upstream demo`  

`git subtree pull --prefix=demo --squash demo`  
