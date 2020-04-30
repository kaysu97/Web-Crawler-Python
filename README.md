# Web-Crawler-Python
Use python beautifulSoup and selenium to crawl the web information and store data in mongodb atlas.
## Introduction
Crawler target is "https://rent.591.com.tw/?kind=0&region=1".
This website has a lot of rental information. And I use beautifulsoup to read the html label and selenium to change the different pages.
![](https://i.imgur.com/9Va34bR.png)
![](https://i.imgur.com/MwfD7GC.png)
Then Let's get started!
## Implementation Steps
Our step:
1. Run the specific region
2. Choose page
3. Crawl the html label on this page and get the rent information list.
4. Request each one of the rental information by Get method.
5. Store data in Mongodb Atlas.
6. Use flask python API to get the rental info by filtering the telephone number you assigned

The information we want to crawl includes
* gender limitation 
* who publish this rental info
* house status
* house type
* publisher contact info
* publisher last name and rental price

There are string problems we need to fix it like some rental price mixed with characters or blank spaces, so I also do data process before storing data into mongodb.
![](https://i.imgur.com/PIrPFyP.png)

After insert data into mongodb, you'll see data in your collection.
![](https://i.imgur.com/99sDNwF.png)

And you can get the data through api
![](https://i.imgur.com/w0929JV.png)



