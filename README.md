# React Chat

React Native simple app for chatting

### Requirements
- React Native
- Python

### Installation
- Inside the repository
``` shell
cd app
npm i
react-native run-android
react-native start
```

- For the server side

``` shell
python -m server
```

#### Technical decisions
- I choose Redis and my message broker and persistence for simplicity and performance. It can also scale horizontally using sharding.
- The server was written using Python+Tornado in order to handle tens of thousands connections simultaneously.
- The client side was written in React Native. This is the side I'm not confortable with, so I waste a lot of time doing things like Websocket connect and components manipulation.
