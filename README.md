# Time-Window Based Anomaly Detection in Public Transport Demand

A production-ready anomaly detection system for public transport passenger demand using statistical methods and vectorized pandas operations.

---

## Project Description

This project demonstrates real-world time-series anomaly detection in public transport systems.

The goal is learning advanced pandas operations, statistical anomaly detection, and scalable data engineering for Big Data platforms.

The system processes 5-minute interval passenger demand data and identifies unusual spikes using Z-score based detection.

---

## Technologies Used

- Python
- Pandas
- NumPy
- Statistical Analysis
- Time-Series Processing

---

## Architecture Overview

```
Raw Data (Route × Time)
         ↓
Feature Engineering (Date, Time-of-Day)
         ↓
Baseline Calculation (Expanding Window)
         ↓
Z-Score Computation
         ↓
Anomaly Detection (Z-score + Percentile)
         ↓
Flagged Anomalies
```

---

## Project Structure

```
transport-anomaly-detection/
├── anomaly_detection.py     # Main implementation
├── anomaly_results.csv       # Output dataset
└── README.md                 # This file
```

---

## How the System Works

### Step 1: Data Generation

Creates synthetic passenger data for:

- 10 bus routes
- 7 consecutive days
- 288 intervals per day (5-minute intervals)
- Total: 20,160 records

### Step 2: Feature Engineering

Extracts temporal features:

- Date component
- Time-of-day component

### Step 3: Baseline Estimation

Calculates historical patterns:

- Uses only previous days' data
- Computes mean and standard deviation per route and time
- Implements expanding window to avoid data leakage

### Step 4: Z-Score Calculation

Measures deviation from baseline using formula:

```
z = (x - μ) / σ
```

### Step 5: Anomaly Detection

Flags unusual patterns when both conditions are met:

- Z-score > 2.5
- Passenger count > 75th percentile

---

## Sample Output

```
Total records: 20,160
Total anomalies: 987
Anomaly rate: 4.89%

route_id  timestamp            passenger_count  z_score  anomaly_flag
R001      2024-01-03 08:15:00  145              3.21     1
R003      2024-01-05 17:30:00  132              2.87     1
R007      2024-01-06 08:45:00  128              3.45     1
```

---

## Key Features

### Vectorized Operations

- No loops - all operations use pandas/numpy vectorization
- Scalable - can handle millions of records
- Fast - optimized for performance

### Time-Aware Baseline

Uses expanding window with shift to ensure baseline uses only historical data:

```python
df['baseline_mean'] = grouped.transform(lambda x: x.shift(1).expanding().mean())
```

### Dual Anomaly Criteria

Combines statistical and percentile-based detection:

- Statistical: Z-score > 2.5 (high deviation)
- Practical: Above 75th percentile (actually high demand)

---

## Data Patterns

### Time-of-Day Patterns

- Morning Rush (7-9 AM): High demand (~50 passengers)
- Evening Rush (5-7 PM): High demand (~45 passengers)
- Midday (11-2 PM): Moderate demand (~30 passengers)
- Night (10 PM-6 AM): Low demand (~5 passengers)

### Variations

- Route-specific demand levels
- Weekend reduction (30% lower)
- Random noise and injected anomalies

---

## Learning Outcomes

This project teaches:

### Advanced Pandas Operations

- groupby() + transform()
- expanding() windows
- Vectorized boolean operations

### Time-Series Processing

- Feature extraction from timestamps
- Time-aware baseline calculation
- Handling temporal ordering

### Statistical Methods

- Z-score normalization
- Percentile-based filtering
- Outlier detection

### Data Engineering Best Practices

- No loops (scalable code)
- Memory-efficient operations
- Production-ready pipelines

---

## Real-World Applications

Similar techniques are used in:

- Public Transport: Demand forecasting and capacity planning
- Cloud Infrastructure: Resource usage anomaly detection
- Finance: Fraud detection and unusual transaction alerts
- E-commerce: Traffic spike detection
- IoT: Sensor data anomaly identification

---

## Requirements

```
pandas>=1.5.0
numpy>=1.23.0
```

---

## Usage

```bash
python anomaly_detection.py
```

Output will be saved to `anomaly_results.csv`

---

## Output Schema

| Column          | Type     | Description                          |
| --------------- | -------- | ------------------------------------ |
| route_id        | string   | Bus route identifier                 |
| timestamp       | datetime | Observation timestamp                |
| passenger_count | int      | Number of passengers observed        |
| baseline_mean   | float    | Historical mean for this time slot   |
| baseline_std    | float    | Historical standard deviation        |
| z_score         | float    | Standardized deviation from baseline |
| anomaly_flag    | int      | 1 if anomaly detected, 0 otherwise   |

---

## Constraint Validation

The code meets all assignment requirements:

- No iterrows() or itertuples()
- No explicit Python for loops
- Uses groupby() + transform()
- Uses expanding() for time-aware calculation
- All NumPy operations are vectorized
- Baseline uses only previous days' data

---

## Performance Benefits

Vectorized operations are approximately 100x faster than loops:

- Loop approach: ~60 seconds for 20K records
- Vectorized approach: ~0.6 seconds for 20K records

---

## Key Insights

### Why Expanding Window?

- Uses all available historical data
- Baseline improves over time
- More stable than fixed windows

### Why Z-Score + Percentile?

- Z-score alone: May flag low-demand outliers
- Percentile alone: Misses statistical anomalies
- Combined: High confidence in flagged anomalies

---

## Bonus Enhancements

Potential extensions:

1. Configurable Window: Modify baseline to use last K days only
2. PySpark Implementation: Scale to distributed processing
3. Visualization: Plot anomalies over time
4. ML Comparison: Compare with Isolation Forest or LSTM

---

## Use Cases

- Data engineering portfolio projects
- Big Data interview preparation
- Pandas proficiency demonstration
- Time-series analysis learning
- Resume and GitHub showcase
