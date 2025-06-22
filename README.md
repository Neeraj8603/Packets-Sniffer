# Network Anomaly Detection System

![Network Security](https://img.shields.io/badge/Network-Security-blue) ![Autoencoder](https://img.shields.io/badge/Model-Autoencoder-green) ![Python](https://img.shields.io/badge/Language-Python-yellow)

A comprehensive network anomaly detection system using various autoencoder architectures to identify suspicious patterns in network traffic logs.

## Features

- **Universal log parser** that automatically detects and extracts features from different log formats
- **Multiple autoencoder architectures** including basic, sparse, variational, and stacked autoencoders
- **Automated feature engineering** with intelligent handling of numeric and categorical data
- **Anomaly scoring** based on reconstruction error with percentile-based thresholding
- **Model comparison** to select the best performing architecture automatically
- **Practical output** with anomaly flags and scores while preserving original log data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/network-anomaly-detection.git
cd network-anomaly-detection
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Training and Detection

```python
from detector import NetworkAnomalyDetector

# Initialize detector (95th percentile threshold)
detector = NetworkAnomalyDetector(threshold_percentile=95)

# Train on log files
log_files = ["logs/log1.txt", "logs/log2.txt"]
df = detector.train(log_files, epochs=50, batch_size=32)

# Save results
detector.save_results(df, "anomaly_results.csv")
```

### Analyzing New Data

```python
# After initial training, analyze new logs
new_results = detector.analyze_new_data(["new_logs/log3.txt"])
detector.save_results(new_results, "new_anomalies.csv")
```

## Model Architectures

1. **Basic Autoencoder**: Simple encoder-decoder structure
2. **Sparse Autoencoder**: With L1 regularization for feature selection
3. **Variational Autoencoder**: Probabilistic approach to encoding
4. **Stacked Autoencoder**: Deep architecture with multiple hidden layers

The system automatically selects the best performing model based on reconstruction accuracy.

## Input Format

The system can parse logs containing:
- Timestamps (multiple formats supported)
- MAC addresses (source and destination)
- IP addresses (both IPv4 and IPv6)
- Port numbers
- Packet lengths
- Payload data (hexadecimal)
- Protocol information

## Output

The system generates CSV files containing:
- All original log data
- Anomaly flag (True/False)
- Anomaly score (reconstruction error)

Sample output columns:
- timestamp
- src_mac
- dst_mac
- src_ip
- src_port
- dst_ip
- dst_port
- packet_length
- payload_sum
- payload_len
- Anomaly
- Anomaly_Score

## Requirements

- Python 3.6+
- pandas
- numpy
- scikit-learn
- tensorflow (or tensorflow-cpu)
- re (built-in)
- time (built-in)
- os (built-in)
- collections (built-in)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT License](LICENSE)
