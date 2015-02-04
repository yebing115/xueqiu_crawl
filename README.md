# xueqiu_crawl
========
## usage   
install [pyspider](https://github.com/binux/pyspider)   
install mongodb  
**use you own cookies, change it in pyspider projects and xueqiu_cube_crawl.py**  
in this directory run   
* `pyspider`

open localhost:5000   
do the xueqiu_user crawl project   
when you have enough user data run   
* `python xueqiu_import.py`   

this will import the result data to mongodb   
run   
* `python xueqiu_cube_crawl.py`

this will fetch every user's cube data

then do the xueqiu_cube crawl project. After that, you have every cube detail data in mongodb
