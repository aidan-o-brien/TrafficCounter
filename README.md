# Traffic Counter

This project was a coursework for Software Technologies for Data Science during my MSc Data Science. For the project, I created an app that allowed users to count traffic at different locations in the city. Users would log-in using their username and password and then proceed to add records of traffic that they observe. Finally, the user could view their session summary before logging out. 

The application uses Python, SQL, HTML, CSS and JS. The SQL database stores information about each session that the user logs in. `task8_out.py` and `task9_out.py` both query the database to provide summary statistics. The former indicates the number of each type of vehicle observed within a given time frame, whilst the latter indicates the total number of hours each user was involved in counting traffic. For additional functionality, `task8_in.py` and `task9_in.py` both allow for bulk data entry through csv files.

Grade achieved: 98% (distinction).

## Pages

| Log-in | Traffic capture | Session summary |
| ----- | ----- | ----- |
| <img src="https://user-images.githubusercontent.com/71706696/141979809-5feb04da-fe95-4ec5-9b4a-05d93027cf8b.png" width="300" /> | <img src="https://user-images.githubusercontent.com/71706696/141979801-5e9d9c4a-3096-45c7-bd8e-9e06d930eeb1.png" width="300" /> | <img src="https://user-images.githubusercontent.com/71706696/141979818-5e074cc6-d329-4694-ad30-933373578fc1.png" width="300" /> |

## Installation and Requirements

To use the code, clone the repository with the following:

```
git clone https://github.com/aidan-o-brien/TrafficCounter
```

__NOTE:__

After running the app with `python server.py`, you will need to open http://127.0.0.1:8081/ in a web browser of your choice.

The following requirements are listed in the `requirements.txt` file:

+ `pandas==1.1.5`
