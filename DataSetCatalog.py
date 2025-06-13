#!/usr/bin/env python3
“””
Dataset Catalog Backend API
Flask application with WebSocket support for real-time communication
“””

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import uuid
from datetime import datetime
import logging

# Configure logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

# Initialize Flask app

app = Flask(**name**)
app.config[‘SECRET_KEY’] = ‘your-secret-key-here’  # Change in production

# Enable CORS for all domains (adjust for production)

CORS(app, origins=”*”)

# Initialize SocketIO

socketio = SocketIO(app, cors_allowed_origins=”*”, logger=True, engineio_logger=True)

# Sample dataset catalog (in production, this would come from a database)

SAMPLE_DATASETS = [
{
“id”: “ds-001”,
“name”: “Customer Analytics Dataset”,
“description”: “Comprehensive customer behavior analytics data including purchase patterns, demographics, and engagement metrics.”,
“size”: “2.3 GB”,
“type”: “CSV”,
“last_updated”: “2024-06-10”,
“status”: “available”,
“tags”: [“analytics”, “customer”, “behavior”]
},
{
“id”: “ds-002”,
“name”: “Sales Performance Data”,
“description”: “Historical sales data with quarterly performance metrics, regional breakdowns, and product category analysis.”,
“size”: “1.8 GB”,
“type”: “JSON”,
“last_updated”: “2024-06-12”,
“status”: “available”,
“tags”: [“sales”, “performance”, “metrics”]
},
{
“id”: “ds-003”,
“name”: “Market Research Survey”,
“description”: “Consumer sentiment analysis from quarterly market research surveys including brand perception and competitive analysis.”,
“size”: “950 MB”,
“type”: “Excel”,
“last_updated”: “2024-06-08”,
“status”: “available”,
“tags”: [“market”, “research”, “survey”]
},
{
“id”: “ds-004”,
“name”: “Financial Transactions Log”,
“description”: “Anonymized financial transaction data for fraud detection and pattern analysis research.”,
“size”: “4.2 GB”,
“type”: “Parquet”,
“last_updated”: “2024-06-13”,
“status”: “processing”,
“tags”: [“financial”, “transactions”, “security”]
},
{
“id”: “ds-005”,
“name”: “IoT Sensor Network Data”,
“description”: “Time-series data from industrial IoT sensors including temperature, pressure, and vibration measurements.”,
“size”: “6.7 GB”,
“type”: “Time Series”,
“last_updated”: “2024-06-11”,
“status”: “available”,
“tags”: [“iot”, “sensors”, “industrial”]
}
]

# In-memory storage for dataset requests (use database in production)

dataset_requests = []

class DatasetService:
“”“Service class to handle dataset operations”””

```
@staticmethod
def get_all_datasets():
    """Retrieve all available datasets"""
    try:
        logger.info("Fetching all datasets")
        return {
            "success": True,
            "datasets": SAMPLE_DATASETS,
            "count": len(SAMPLE_DATASETS)
        }
    except Exception as e:
        logger.error(f"Error fetching datasets: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@staticmethod
def request_dataset(dataset_id, user_info=None):
    """Process a dataset request"""
    try:
        # Find the dataset
        dataset = next((ds for ds in SAMPLE_DATASETS if ds["id"] == dataset_id), None)
        
        if not dataset:
            return {
                "success": False,
                "error": f"Dataset with ID '{dataset_id}' not found"
            }
        
        # Check if dataset is available
        if dataset.get("status") != "available":
            return {
                "success": False,
                "error": f"Dataset '{dataset['name']}' is not currently available (Status: {dataset.get('status', 'unknown')})"
            }
        
        # Create request record
        request_record = {
            "request_id": str(uuid.uuid4()),
            "dataset_id": dataset_id,
            "dataset_name": dataset["name"],
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "user_info": user_info or {}
        }
        
        # Store request (in production, save to database)
        dataset_requests.append(request_record)
        
        logger.info(f"Dataset request created: {request_record['request_id']} for dataset {dataset_id}")
        
        return {
            "success": True,
            "message": f"Dataset '{dataset['name']}' has been requested successfully",
            "request_id": request_record["request_id"],
            "dataset_info": {
                "id": dataset["id"],
                "name": dataset["name"],
                "size": dataset["size"],
                "type": dataset["type"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing dataset request: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@staticmethod
def get_request_status(request_id):
    """Get the status of a dataset request"""
    try:
        request_record = next((req for req in dataset_requests if req["request_id"] == request_id), None)
        
        if not request_record:
            return {
                "success": False,
                "error": "Request not found"
            }
        
        return {
            "success": True,
            "request": request_record
        }
        
    except Exception as e:
        logger.error(f"Error fetching request status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

# WebSocket Event Handlers

@socketio.on(‘connect’)
def handle_connect():
“”“Handle client connection”””
logger.info(f”Client connected: {request.sid}”)
emit(‘connection_response’, {
‘success’: True,
‘message’: ‘Connected to Dataset Catalog API’,
‘timestamp’: datetime.now().isoformat()
})

@socketio.on(‘disconnect’)
def handle_disconnect():
“”“Handle client disconnection”””
logger.info(f”Client disconnected: {request.sid}”)

@socketio.on(‘get_all_datasets’)
def handle_get_all_datasets():
“”“Handle request to get all datasets”””
logger.info(f”Get all datasets requested by client: {request.sid}”)

```
try:
    result = DatasetService.get_all_datasets()
    emit('datasets_response', result)
    
except Exception as e:
    logger.error(f"Error handling get_all_datasets: {str(e)}")
    emit('datasets_response', {
        'success': False,
        'error': str(e)
    })
```

@socketio.on(‘request_dataset’)
def handle_request_dataset(data):
“”“Handle dataset request”””
logger.info(f”Dataset request from client {request.sid}: {data}”)

```
try:
    dataset_id = data.get('dataset_id')
    user_info = data.get('user_info', {})
    
    if not dataset_id:
        emit('dataset_request_response', {
            'success': False,
            'error': 'Dataset ID is required'
        })
        return
    
    result = DatasetService.request_dataset(dataset_id, user_info)
    emit('dataset_request_response', result)
    
    # Optionally notify all clients about the new request
    if result['success']:
        socketio.emit('dataset_request_notification', {
            'message': f"New dataset request: {result['dataset_info']['name']}",
            'request_id': result['request_id'],
            'timestamp': datetime.now().isoformat()
        }, broadcast=True, include_self=False)
    
except Exception as e:
    logger.error(f"Error handling request_dataset: {str(e)}")
    emit('dataset_request_response', {
        'success': False,
        'error': str(e)
    })
```

@socketio.on(‘get_request_status’)
def handle_get_request_status(data):
“”“Handle request status inquiry”””
logger.info(f”Request status inquiry from client {request.sid}: {data}”)

```
try:
    request_id = data.get('request_id')
    
    if not request_id:
        emit('request_status_response', {
            'success': False,
            'error': 'Request ID is required'
        })
        return
    
    result = DatasetService.get_request_status(request_id)
    emit('request_status_response', result)
    
except Exception as e:
    logger.error(f"Error handling get_request_status: {str(e)}")
    emit('request_status_response', {
        'success': False,
        'error': str(e)
    })
```

# Traditional REST API endpoints (optional, for testing)

@app.route(’/api/health’, methods=[‘GET’])
def health_check():
“”“Health check endpoint”””
return {
‘status’: ‘healthy’,
‘timestamp’: datetime.now().isoformat(),
‘version’: ‘1.0.0’
}

@app.route(’/api/datasets’, methods=[‘GET’])
def get_datasets_rest():
“”“REST endpoint to get all datasets”””
result = DatasetService.get_all_datasets()
return result

@app.route(’/api/datasets/<dataset_id>/request’, methods=[‘POST’])
def request_dataset_rest(dataset_id):
“”“REST endpoint to request a dataset”””
user_info = request.get_json() or {}
result = DatasetService.request_dataset(dataset_id, user
