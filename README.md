# Flask-Api

Flask Api Store
This skeleton can be used for any type of project desired to be deployed.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Deployment](#deployment)
  - [Deploying on Render.com](#deploying-on-rendercom)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- Docker / Docker-compose compatible
- Password encryption on server side
- User authentication with JWT
- SQL database enabled
- Automatic documentation with Swagger UI

## Technologies Used

- **Python**
- **Flask**
- **Flask-Smorest**
- **Flask-SQLAlchemy**
- **Docker**
- **PostgreSQL**
- **Gunicorn**
- **Marshmallow**


## Getting Started

### Prerequisites

Make sure you have the following software installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) [Python 3.x](https://www.python.org/downloads/) for local development
- .env file configuration or env_config.py file with databse_url,mail_gun key or any other personal configuration

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rafalm0/Flask-store
    cd Flask-store
    ```

2. (Optional) Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. (Optional) Set up your environment variables in a `.env` file.
    If database not setup, the project will create an sqlite automatically

### Running the Application

You can run the application using Docker:

```bash
docker run -dp 5000:5000 -w /app -v $PWD/:/app my_api
```

This command does the following:
- `-d`: Runs the container in detached mode
- `-p 5000:5000`: Maps port 5000 on your host to port 5000 in the container
- `-w /app`: Sets the working directory inside the container to `/app`
- `-v $PWD/:/app`: Mounts the current directory into the container at `/app`

## Deployment

### Deploying on Render.com

1. Sign up for a [Render.com](https://render.com/) account.
2. Create a new web service:
   - Choose the **Docker** option.
   - Connect your GitHub repository.
3. Configure the environment variables required by your application in Render's dashboard.
4. Click **Create Web Service** to deploy your API.

You can also host a PostgreSQL database on Render:
1. Create a new database in Render.
2. Update your application's .env to connect to this database with its URL.

For background worker:
1. Enable its usage in app.py
2. Create a background worker on render.com
3. on docker command use : /bin/bash -c cd /app && rq worker -c settings

## API Endpoints


Here’s a list of already available API endpoints with their methods.

obs:. Any endpoint and documentation can be further viewed after deployment with: {your_project_url}/swagger-ui

### Example Endpoint

**GET** `{url}/store`

- **Description**: Retrieve a list of stores.
- **Request Example**:
    ```bash
    curl -X GET http://localhost:5000/store
    ```

## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a feature branch:
    ```bash
    git checkout -b feature/YourFeature
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add your message here"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/YourFeature
    ```
5. Open a pull request.

## License

## Contact

- Rafael Almeida Albuquerque - [almeida_36@hotmail.com](mailto:almeida_36@hotmail.com)
- GitHub: [Rafalm0](https://github.com/rafalm0)
