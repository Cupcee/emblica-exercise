# Sessionization

## Task description
Your task is to write a program that reads **events** from `stdin` and outputs **sessions** to `stdout`
This processing step is called **sessionization**

![Imgur](https://i.imgur.com/Eu6lZIX.png)

Idea is to group events to sessions so there can be advanced analytics on those sessions.
The events comes from music player (like spotify) from various user agents. All of the users are recognized with unique identifier (`uid`) and each of the tracks have unique `content_id`

We cannot answer questions like _"What was the most listened song in last week?"_ or _"How big was the peak of simultaneous listeners with content_id 18 last week?"_ just by looking the **events** but sessioning them will give us great dataset to answer the queries.

![Imgur](https://i.imgur.com/KbR7Bc3.png)


## Events

Events are `JSON`-formatted objects separated by newlines (`\n`)

You can assume that all the events always come on time and with monotonically increasing timestamp.
Here is an example of (pretty formatted) event.
All fields are described down below, all of them are mandatory
```JSON
{
  "timestamp": 123,
  "event_type": "track_heartbeat",
  "user_id": "A",
  "content_id": "T1001"
}
```

| Field      | Type    | Description                                                                                         |
|------------|---------|-----------------------------------------------------------------------------------------------------|
| timestamp  | integer | Timestamp as seconds, can be understood as unix epoch like field but with arbitrary starting point. |
| event_type | string  | Enum of different event types, see table below for descriptions                                     |
| user_id    | string  | identifier for the user                                                                             |
| content_id | string  | identifier for the content                                                                          |

### Event types

| Event type      | Description                                                                                         |
|-----------------|-----------------------------------------------------------------------------------------------------|
| stream_start    | Stream start event, occurs every time user starts streaming some content, should be the first event |
| ad_start        | Advertisement start, marks start of the ad                                                          |
| ad_end          | Advertisement end, marks the end of the previous start pair                                         |
| track_start     | Track playing started                                                                               |
| track_heartbeat | Every ~ten seconds of played track there will be heartbeat event                                    |
| pause           | If user pauses the track it will send pause-event. Ads cannot be paused                             |
| play            | If user continues the track it will send play-event. Must happen after pause-event                  |
| track_end       | When track ends this event is dispatched                                                            |
| stream_end      | When stream ends this event is dispatched                                                           |


Here you can see events of two closed and one just opened sessions.
Green line is logical session "gap" between the events. When the event is closed the sessionizer must create and dispatch an complete session. The dispatch of the complete session including previous events is indicated by `output` column in following picture.
![Imgur](https://i.imgur.com/7W5Sqw5.png)


# Sessions

Sessions can have multiple advertisements (ad_start, ad_end -pairs), multiple pauses (pause, play -pairs) and single track (start,heartbeats,end)

You have to always consider user shutting down the session in any moment and then you cannot expect the `end_` events to arrive ever. In that case session is timeouted in **1 minute** (60s) and the best possible approximation of the closed session is dispatched.

Below is the closed sessions from the sessions described in table above.


| user_id | content_id | session_start | session_end | total_time | track_playtime | event_count | ad_count |
|---------|------------|---------------|-------------|------------|----------------|-------------|----------|
| A       | 10001      | 0             | 64          | 64         | 47             | 14          | 2        |
| A       | 10001      | 100           | 117         | 17         | 10             | 5           | 1        |


Pay attention that the third session is still open.

Example of output, JSON-formatted event
```JSON
{
  "user_id": "A",
  "content_id": "10001",
  "session_start": 0,
  "session_end": 64,
  "total_time": 64,
  "track_playtime": 47,
  "event_count": 14,
  "ad_count": 2
}
```

## Summary: requirements

- Sessionization by (user_id, content_id)
- Sessions must contain properties shown above, calculated from events
- Session gap (timeout) must be 60s
- Sessions can be incomplete from the end
- Bonus: Process also sessions with missing events from the start
