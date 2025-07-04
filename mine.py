{
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "import re\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import time\n",
        "from sklearn.preprocessing import MinMaxScaler\n",
        "from sklearn.metrics import mean_squared_error\n",
        "from tensorflow.keras.models import Model\n",
        "from tensorflow.keras.layers import Input, Dense, Lambda\n",
        "from tensorflow.keras.optimizers import Adam\n",
        "from tensorflow.keras import regularizers\n",
        "import tensorflow.keras.backend as K\n",
        "import os"
      ],
      "metadata": {
        "id": "XJ5r0OMgD5rq"
      },
      "execution_count": 1,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Load and preprocess log data from multiple files\n",
        "def parse_logs(file_paths):\n",
        "    data = []\n",
        "    for file_path in file_paths:\n",
        "        with open(file_path, 'r') as file:\n",
        "            entry = {}\n",
        "            for line in file:\n",
        "                line = line.strip()\n",
        "\n",
        "                if re.match(r'^[A-Za-z]{3} \\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4}$', line):\n",
        "                    if entry:\n",
        "                        data.append(entry)\n",
        "                        entry = {}\n",
        "                    entry['timestamp'] = line\n",
        "                elif 'Packet length' in line:\n",
        "                    entry['packet_length'] = int(re.search(r'\\d+', line).group())\n",
        "                elif 'Source:' in line:\n",
        "                    entry['source_ip'] = line.split(': ')[1]\n",
        "                elif 'Dest:' in line:\n",
        "                    entry['dest_ip'] = line.split(': ')[1]\n",
        "                elif 'Payload (hex):' in line:\n",
        "                    hex_payload = line.split(': ')[1].split()\n",
        "                    entry['payload_sum'] = sum(int(byte, 16) for byte in hex_payload)\n",
        "                    entry['payload_len'] = len(hex_payload)\n",
        "\n",
        "            if entry:\n",
        "                data.append(entry)\n",
        "\n",
        "    df = pd.DataFrame(data)\n",
        "    df.fillna({'source_ip': '0.0.0.0', 'dest_ip': '0.0.0.0', 'packet_length': 0, 'payload_sum': 0, 'payload_len': 0}, inplace=True)\n",
        "    return df\n"
      ],
      "metadata": {
        "id": "RK8v2ncBEKlf"
      },
      "execution_count": 2,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Convert IPs to numerical features\n",
        "def ip_to_int(ip):\n",
        "    try:\n",
        "        parts = ip.split('.')\n",
        "        return sum(int(part) * (256 ** i) for i, part in enumerate(reversed(parts)))\n",
        "    except:\n",
        "        return 0"
      ],
      "metadata": {
        "id": "5sxsywx3EPIK"
      },
      "execution_count": 3,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# List all uploaded log files with absolute paths\n",
        "log_files = [\n",
        "    \"log.txt\",\n",
        "    \"log1.txt\",\n",
        "    \"log2.txt\",\n",
        "    \"logfile_compressed.txt\",\n",
        "    \"test.txt\"\n",
        "]"
      ],
      "metadata": {
        "id": "wbFKPBiqESzo"
      },
      "execution_count": 4,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "df = parse_logs(log_files)\n",
        "df['source_ip'] = df['source_ip'].apply(ip_to_int)\n",
        "df['dest_ip'] = df['dest_ip'].apply(ip_to_int)"
      ],
      "metadata": {
        "id": "k8rS7td8EWHz"
      },
      "execution_count": 5,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Normalize features\n",
        "scaler = MinMaxScaler()\n",
        "df_scaled = scaler.fit_transform(df[['packet_length', 'source_ip', 'dest_ip', 'payload_sum', 'payload_len']])\n",
        "\n",
        "input_dim = df_scaled.shape[1]"
      ],
      "metadata": {
        "id": "8F3gI3zJEZn0"
      },
      "execution_count": 6,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def detect_anomalies(reconstructions, threshold_percentile=95):\n",
        "    anomaly_scores = np.mean(np.abs(df_scaled - reconstructions), axis=1)\n",
        "    threshold = np.percentile(anomaly_scores, threshold_percentile)\n",
        "    return anomaly_scores > threshold"
      ],
      "metadata": {
        "id": "1qClCiBeEcrO"
      },
      "execution_count": 7,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def build_autoencoder():\n",
        "    input_layer = Input(shape=(input_dim,))\n",
        "    encoded = Dense(32, activation='relu')(input_layer)  # Adjust the number of units as needed\n",
        "    decoded = Dense(input_dim, activation='sigmoid')(encoded)\n",
        "    autoencoder = Model(input_layer, decoded)\n",
        "    return autoencoder"
      ],
      "metadata": {
        "id": "aDPGHQZCGAyq"
      },
      "execution_count": 11,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def build_sparse_autoencoder():\n",
        "    input_layer = Input(shape=(input_dim,))\n",
        "    encoded = Dense(32, activation='relu', activity_regularizer=regularizers.l1(10e-5))(input_layer)\n",
        "    decoded = Dense(input_dim, activation='sigmoid')(encoded)\n",
        "    autoencoder = Model(input_layer, decoded)\n",
        "    return autoencoder\n",
        "\n",
        "def build_variational_autoencoder():\n",
        "    # This is a placeholder, needs implementation for VAE\n",
        "    return build_autoencoder()\n",
        "\n",
        "def build_stacked_autoencoder():\n",
        "    # This is a placeholder, needs implementation for Stacked AE\n",
        "    return build_autoencoder()\n"
      ],
      "metadata": {
        "id": "swb33IUZF2Dx"
      },
      "execution_count": 9,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "models = {\n",
        "    'AutoEncoder': build_autoencoder(),\n",
        "    'Sparse AutoEncoder': build_sparse_autoencoder(),\n",
        "    'Variational AutoEncoder': build_variational_autoencoder(),\n",
        "    'Stacked AutoEncoder': build_stacked_autoencoder()\n",
        "}"
      ],
      "metadata": {
        "id": "fgPpW2ujEfzJ"
      },
      "execution_count": 12,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "results = {}"
      ],
      "metadata": {
        "id": "H77-zczMGLcK"
      },
      "execution_count": 13,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "for name, model in models.items():\n",
        "    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')\n",
        "    start_time = time.time()\n",
        "    model.fit(df_scaled, df_scaled, epochs=10, batch_size=8, shuffle=True, validation_split=0.2, verbose=0)\n",
        "    training_time = time.time() - start_time\n",
        "    reconstructions = model.predict(df_scaled)\n",
        "    mse = mean_squared_error(df_scaled, reconstructions)\n",
        "    accuracy = 1 - mse\n",
        "    results[name] = {'Accuracy': accuracy, 'MSE': mse, 'Training Time': training_time}\n",
        "    print(f\"{name}: Accuracy={accuracy:.4f}, MSE={mse:.6f}, Training Time={training_time:.2f}s\")"
      ],
      "metadata": {
        "id": "YzLLJEYMGT-v",
        "outputId": "1179600b-ab15-4611-c9e9-1dc1f5f63d5e",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "execution_count": 15,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\u001b[1m785/785\u001b[0m \u001b[32m━━━━━━━━━━━━━━━━━━━━\u001b[0m\u001b[37m\u001b[0m \u001b[1m1s\u001b[0m 1ms/step\n",
            "AutoEncoder: Accuracy=0.9740, MSE=0.025965, Training Time=70.06s\n",
            "\u001b[1m785/785\u001b[0m \u001b[32m━━━━━━━━━━━━━━━━━━━━\u001b[0m\u001b[37m\u001b[0m \u001b[1m1s\u001b[0m 1ms/step\n",
            "Sparse AutoEncoder: Accuracy=0.9719, MSE=0.028061, Training Time=87.39s\n",
            "\u001b[1m785/785\u001b[0m \u001b[32m━━━━━━━━━━━━━━━━━━━━\u001b[0m\u001b[37m\u001b[0m \u001b[1m1s\u001b[0m 1ms/step\n",
            "Variational AutoEncoder: Accuracy=0.9742, MSE=0.025812, Training Time=73.65s\n",
            "\u001b[1m785/785\u001b[0m \u001b[32m━━━━━━━━━━━━━━━━━━━━\u001b[0m\u001b[37m\u001b[0m \u001b[1m1s\u001b[0m 1ms/step\n",
            "Stacked AutoEncoder: Accuracy=0.9742, MSE=0.025807, Training Time=78.49s\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "best_model = max(results, key=lambda k: results[k]['Accuracy'])\n",
        "print(f\"Best Model: {best_model} with Accuracy {results[best_model]['Accuracy']:.4f}\")"
      ],
      "metadata": {
        "id": "G66t5ANcGowp",
        "outputId": "932ed8c4-538c-4ba1-9fbf-55a9f9297233",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "execution_count": 16,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Best Model: Stacked AutoEncoder with Accuracy 0.9742\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "reconstructions = models[best_model].predict(df_scaled)\n",
        "df['Anomaly'] = detect_anomalies(reconstructions)\n",
        "df.to_csv('log_anomalies.csv', index=False)\n",
        "print(\"Anomaly detection complete. Results saved to log_anomalies.csv.\")"
      ],
      "metadata": {
        "id": "nbYTfjIzGqOg",
        "outputId": "ce17705e-38e5-4c81-938f-acd82e8a4a67",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "execution_count": 17,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\u001b[1m785/785\u001b[0m \u001b[32m━━━━━━━━━━━━━━━━━━━━\u001b[0m\u001b[37m\u001b[0m \u001b[1m1s\u001b[0m 1ms/step\n",
            "Anomaly detection complete. Results saved to log_anomalies.csv.\n"
          ]
        }
      ]
    }
  ],
  "metadata": {
    "colab": {
      "name": "Welcome To Colab",
      "provenance": []
    },
    "kernelspec": {
      "display_name": "Python 3",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 0
}
