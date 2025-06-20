# Kite Trading API

A Flask-based REST API for Zerodha Kite trading operations with Swagger documentation.

## Features

- Login to Zerodha Kite
- Get instruments data
- Fetch historical data
- Place, modify, and cancel orders
- Get holdings, positions, and margins
- User profile information
- Interactive Swagger documentation

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python kite_api.py
```

3. Access the API:
- API: http://localhost:5000
- Swagger UI: http://localhost:5000/swagger

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Connect your repository to Render
3. Render will automatically detect the `render.yaml` file and deploy your service

### Option 2: Manual Deployment

1. Create a new Web Service on Render
2. Connect your Git repository
3. Configure the service:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or choose your preferred plan)

## API Endpoints

- `POST /login` - Login to Kite
- `GET /instruments` - Get instruments data
- `GET /historical-data` - Get historical data
- `POST /place-order` - Place a new order
- `GET /orders` - Get all orders
- `GET /holdings` - Get holdings
- `GET /positions` - Get positions
- `GET /profile` - Get user profile
- `GET /margins` - Get user margins
- `PUT /modify-order` - Modify an existing order
- `DELETE /cancel-order` - Cancel an existing order

## Authentication

The API uses enctoken-based authentication. After login, include the enctoken in the `X-Enctoken` header for subsequent requests.

## Environment Variables

- `PORT` - Port number (default: 5000)

## Dependencies

- Flask 2.3.3
- flask-swagger-ui 4.11.1
- requests 2.31.0
- gunicorn 21.2.0
- python-dateutil 2.8.2