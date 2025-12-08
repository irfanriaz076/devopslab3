#!/usr/bin/env python3
"""
Cybersecurity Malware Detection Inference Script
CYBER-DEF25 Challenge

This script loads the trained model, analyzes network logs,
detects potential threats, and outputs results to alerts.csv
"""

import os
import pickle
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPUT_DIR = Path('/input/logs')
OUTPUT_DIR = Path('/output')
MODEL_PATH = Path('/app/model.pkl')
DETECTION_THRESHOLD = float(os.getenv('DETECTION_THRESHOLD', 0.85))


def load_model(model_path: Path):
    """Load the trained cybersecurity model."""
    logger.info(f"Loading model from {model_path}")
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def parse_log_file(log_path: Path) -> pd.DataFrame:
    """Parse network log file and extract features."""
    logger. info(f"Parsing log file: {log_path}")
    
    # Example log parsing - adjust based on your log format
    try:
        # Try reading as CSV first
        df = pd.read_csv(log_path)
    except:
        # Fall back to line-by-line parsing
        logs = []
        with open(log_path, 'r') as f:
            for line in f:
                # Parse log line - customize based on your format
                logs.append({'raw_log': line.strip()})
        df = pd.DataFrame(logs)
    
    logger.info(f"Parsed {len(df)} log entries")
    return df


def extract_features(df: pd.DataFrame) -> np.ndarray:
    """Extract features from parsed logs for model inference."""
    # Feature extraction logic - customize based on your model
    # This is a placeholder implementation
    
    # Example features for network traffic analysis:
    # - Packet size statistics
    # - Connection duration
    # - Protocol type encoding
    # - Port number analysis
    # - Byte frequency distribution
    
    # For demonstration, create random features
    # Replace with actual feature extraction
    n_samples = len(df)
    n_features = 10  # Adjust based on your model
    
    features = np.random. randn(n_samples, n_features)
    return features


def detect_threats(model, features: np. ndarray, threshold: float) -> np.ndarray:
    """Run inference to detect potential threats."""
    logger.info(f"Running threat detection on {len(features)} samples")
    
    try:
        # Get prediction probabilities
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features)[:, 1]
        else:
            probabilities = model.predict(features)
        
        # Apply threshold for classification
        predictions = (probabilities >= threshold).astype(int)
        
        threat_count = predictions.sum()
        logger.info(f"Detected {threat_count} potential threats")
        
        return predictions, probabilities
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise


def generate_alerts(df: pd. DataFrame, predictions: np.ndarray, 
                    probabilities: np.ndarray, output_path: Path):
    """Generate alerts CSV file with detection results."""
    logger.info(f"Generating alerts to {output_path}")
    
    alerts_df = df. copy()
    alerts_df['threat_detected'] = predictions
    alerts_df['threat_probability'] = probabilities
    alerts_df['alert_level'] = pd.cut(
        probabilities,
        bins=[0, 0.5, 0.75, 0.9, 1.0],
        labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    )
    alerts_df['timestamp'] = datetime.now(). isoformat()
    
    # Save to CSV
    alerts_df.to_csv(output_path, index=False)
    logger.info(f"Alerts saved: {len(alerts_df)} entries")
    
    return alerts_df


def main():
    """Main inference pipeline."""
    logger.info("=" * 50)
    logger.info("CYBER-DEF25 Malware Detection System")
    logger. info("=" * 50)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load model
    model = load_model(MODEL_PATH)
    
    # Process all log files in input directory
    log_files = list(INPUT_DIR.glob('*.log')) + \
                list(INPUT_DIR.glob('*.csv')) + \
                list(INPUT_DIR. glob('*.txt'))
    
    if not log_files:
        logger.warning(f"No log files found in {INPUT_DIR}")
        # Create empty alerts file
        pd.DataFrame(columns=[
            'threat_detected', 'threat_probability', 
            'alert_level', 'timestamp'
        ]).to_csv(OUTPUT_DIR / 'alerts.csv', index=False)
        return
    
    all_alerts = []
    
    for log_file in log_files:
        logger.info(f"Processing: {log_file. name}")
        
        # Parse logs
        df = parse_log_file(log_file)
        df['source_file'] = log_file.name
        
        # Extract features
        features = extract_features(df)
        
        # Detect threats
        predictions, probabilities = detect_threats(
            model, features, DETECTION_THRESHOLD
        )
        
        # Generate alerts
        alerts = generate_alerts(
            df, predictions, probabilities,
            OUTPUT_DIR / f'alerts_{log_file.stem}.csv'
        )
        all_alerts.append(alerts)
    
    # Combine all alerts into single file
    combined_alerts = pd. concat(all_alerts, ignore_index=True)
    combined_alerts.to_csv(OUTPUT_DIR / 'alerts. csv', index=False)
    
    # Summary statistics
    total_threats = combined_alerts['threat_detected'].sum()
    logger.info("=" * 50)
    logger.info("DETECTION SUMMARY")
    logger.info(f"Total logs analyzed: {len(combined_alerts)}")
    logger.info(f"Threats detected: {total_threats}")
    logger.info(f"Detection rate: {total_threats/len(combined_alerts)*100:.2f}%")
    logger. info("=" * 50)


if __name__ == '__main__':
    main()
