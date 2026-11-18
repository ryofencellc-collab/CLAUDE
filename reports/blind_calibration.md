## Calibration: detection rate by strategy type and strength

3 runs per cell. k = planted drift in standard deviations of the affected segment (the blind draw used 0.30–0.45).

| strategy              |    k |   grid_found |   scan_found |   false_alarms |   scan_false | grid_family    |
|:----------------------|-----:|-------------:|-------------:|---------------:|-------------:|:---------------|
| gap_fill              | 0.15 |     0        |     0        |              0 |            0 |                |
| gap_fill              | 0.25 |     0        |     0        |              0 |            1 |                |
| gap_fill              | 0.35 |     0        |     0.333333 |              0 |            0 |                |
| gap_fill              | 0.45 |     0        |     0.333333 |              1 |            0 |                |
| lunch_reversal        | 0.15 |     0        |     0        |              0 |            0 |                |
| lunch_reversal        | 0.25 |     0        |     1        |              0 |            0 |                |
| lunch_reversal        | 0.35 |     0        |     1        |              0 |            0 |                |
| lunch_reversal        | 0.45 |     0        |     1        |              0 |            1 |                |
| narrow_range_breakout | 0.15 |     0.333333 |     0        |              0 |            1 | ORB30          |
| narrow_range_breakout | 0.25 |     0.333333 |     0        |              0 |            0 | ORB30          |
| narrow_range_breakout | 0.35 |     0.666667 |     0.333333 |              0 |            0 | ORB30          |
| narrow_range_breakout | 0.45 |     1        |     1        |              0 |            0 | ORB15,ORB30    |
| orb_continuation      | 0.15 |     0        |     0.333333 |              0 |            0 |                |
| orb_continuation      | 0.25 |     0.333333 |     0.333333 |              0 |            0 | ORB15          |
| orb_continuation      | 0.35 |     1        |     0.666667 |              0 |            0 | ORB15          |
| orb_continuation      | 0.45 |     1        |     1        |              0 |            1 | ORB15,ORB30    |
| overnight_momentum    | 0.15 |     0        |     0        |              0 |            0 |                |
| overnight_momentum    | 0.25 |     1        |     1        |              0 |            0 | ORB15,ORB5     |
| overnight_momentum    | 0.35 |     0.666667 |     1        |              0 |            0 | ORB15,ORfade15 |
| overnight_momentum    | 0.45 |     1        |     1        |              0 |            0 | GapGo0.2,ORB15 |
| power_hour_trend      | 0.15 |     0        |     0        |              0 |            0 |                |
| power_hour_trend      | 0.25 |     0.666667 |     1        |              0 |            0 | PowerHour0.3   |
| power_hour_trend      | 0.35 |     1        |     1        |              0 |            0 | PowerHour0.3   |
| power_hour_trend      | 0.45 |     1        |     1        |              0 |            0 | PowerHour0.3   |
| weekday_drift         | 0.15 |     0        |     0        |              0 |            0 |                |
| weekday_drift         | 0.25 |     0        |     0        |              0 |            0 |                |
| weekday_drift         | 0.35 |     0        |     0        |              0 |            0 |                |
| weekday_drift         | 0.45 |     0        |     1        |              0 |            1 |                |
