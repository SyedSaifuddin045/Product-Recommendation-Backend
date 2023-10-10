# Product-Recommendation-Backend

Recommended branch to clone ```multithread```  
```main``` branch works on single thread and thus processes results slowly.


Clone the Repo and make sure you have npm and node installed then run:
```
cd Product-Recommendation-Backend
npm install
node server.js
```

The Backend should start running on the PORT : 3500

If there are any issues running this.The project also contains a docker file that would create an image for you.
```
cd Product-Recommendation-Backend
docker build -t Product-Recommendation-Backend:1.0 .
docker run -d Product-Recommendation-Backend:1.0
```

### If any issues are found please open an issue on Github.  
### Contributions are open for everyone.
