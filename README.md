# Video Analysis Agent - README

## Purpose
This application is a "Video Analysis Agent" that allows users to upload video files, analyze their content for objects, and query the video content using natural language to find relevant video frames and timeframes.

## Project Structure
- `frontend/`: ReactJS frontend application.
- `backend/`: Python Flask backend application.
- `docker-compose.yml`: For local development using Docker Compose.
- `.env.example`: Example environment variable file.

## Prerequisites

1.  **Google Cloud Account:** You need a Google Cloud Platform account with billing enabled.
2.  **Google Cloud SDK (gcloud CLI):**  Installed and configured.
3.  **Python 3.9+:**  Installed on your local machine.
4.  **Node.js and npm/yarn:** Installed for frontend development.
5.  **Docker and Docker Compose:** Installed for local development and containerization.

## Setup and Configuration

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd video-analysis-agent
    ```

2.  **Configure Google Cloud:**
    *   **Create Google Cloud Project:** If you don't have one already.
    *   **Enable APIs:** Enable the following Google Cloud APIs in your project:
        *   Vertex AI API
        *   Cloud Storage API
        *   AlloyDB API
        *   Kubernetes Engine API (for deployment)
    *   **Create Cloud Storage Buckets:**
        *   Create two Cloud Storage buckets: one for storing uploaded videos (e.g., `your-video-bucket-name`) and another for storing extracted frames (e.g., `your-frame-bucket-name`).
    *   **Create AlloyDB Instance:** Create an AlloyDB for PostgreSQL instance in your Google Cloud project. Note down the connection details (connection string or individual settings).
    *   **Create Service Account (Recommended for Production):** Create a Google Cloud Service Account with necessary permissions to access:
        *   Vertex AI API
        *   Cloud Storage (Read/Write access to your buckets)
        *   AlloyDB (Client role or similar to connect and query)
        *   Download the Service Account key file in JSON format. For local development using your user credentials via `gcloud auth application-default login` is also possible, but less secure for production.

3.  **Environment Variables:**
    *   Copy `.env.example` to `.env` in the root directory.
    *   Fill in the `.env` file with your Google Cloud project details, API key, bucket names, AlloyDB connection information, and desired video sampling rate.
        *   **`GCP_PROJECT_ID`**: Your Google Cloud Project ID.
        *   **`GCP_REGION`**: Google Cloud region to use (e.g., `us-central1`).
        *   **`GCP_VERTEX_AI_API_KEY`**: Your Google Vertex AI API key (or set up Application Default Credentials if using a Service Account).
        *   **`GCS_BUCKET_NAME_VIDEOS`**: Name of your Cloud Storage bucket for videos.
        *   **`GCS_BUCKET_NAME_FRAMES`**: Name of your Cloud Storage bucket for frames.
        *   **`ALLOYDB_CONNECTION_STRING`** or individual AlloyDB settings (`ALLOYDB_INSTANCE_ID`, `ALLOYDB_DATABASE_NAME`, `ALLOYDB_USER`, `ALLOYDB_PASSWORD`).
        *   **`VIDEO_SAMPLING_RATE`**: Frames per second to sample from videos (integer).

## Running Locally for Debug and Test (using Docker Compose)

1.  **Start Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will build and start both the frontend and backend applications.

2.  **Access the application:** Open your web browser and go to `http://localhost:3000`.

3.  **Backend API:** The backend API will be running at `http://localhost:5000/api`.

4.  **Stop Docker Compose:** To stop the application, run:
    ```bash
    docker-compose down
    ```

## Deploying to Google Cloud (using GKE - Google Kubernetes Engine)

**Note:** Deployment to GKE is more complex and requires further configuration of your Google Cloud project and Kubernetes cluster. This is a high-level outline.

1.  **Containerize Applications:**
    *   Ensure the `backend/Dockerfile` and `frontend/Dockerfile` are configured correctly.
    *   Build Docker images for frontend and backend. You might want to push these images to Google Container Registry (GCR).

2.  **Create a GKE Cluster:** Create a Google Kubernetes Engine cluster in your Google Cloud project.

3.  **Deploy AlloyDB (if not already deployed):**  Ensure your AlloyDB instance is set up and accessible from within your GKE cluster's network (consider using private IP and VPC peering).

4.  **Deploy Cloud Storage Buckets (if not already created):** Your Cloud Storage buckets for videos and frames should be created and configured.

5.  **Kubernetes Deployment and Service Definitions:**
    *   Create Kubernetes Deployment YAML files for the backend and frontend applications.
        *   **Backend Deployment:**  Configure environment variables in the Deployment YAML using Kubernetes Secrets or ConfigMaps to securely pass your Google Cloud API key, AlloyDB connection details, etc. Mount a volume to load the Service Account key file if using that authentication method.
        *   **Frontend Deployment:**  Configure the `REACT_APP_API_BASE_URL` environment variable in the frontend Deployment to point to the backend service within the cluster.
    *   Create Kubernetes Service YAML files to expose the backend and frontend applications.
        *   **Backend Service:** Create a ClusterIP service to expose the backend within the cluster.
        *   **Frontend Service:** Create a LoadBalancer service to expose the frontend to the internet via an external IP address.

6.  **Apply Kubernetes Configurations:** Use `kubectl apply -f <deployment_yaml_file>` and `kubectl apply -f <service_yaml_file>` to deploy your application to the GKE cluster.

7.  **Access the Application:** Once the frontend LoadBalancer service is deployed, get the external IP address assigned to it using `kubectl get service frontend-service -o wide` and access the application in your browser using that IP address.

## Important Notes

*   **Security:** For production deployments, ensure you handle API keys and database credentials securely using Kubernetes Secrets and best practices for secret management in Google Cloud.
*   **Error Handling and Monitoring:** Implement proper error handling, logging, and monitoring for both frontend and backend applications. Consider using Google Cloud Logging and Monitoring.
*   **Scalability and Performance:** For production, consider scaling your GKE cluster and AlloyDB instance based on expected load. Optimize video processing and query performance as needed.
*   **Gemini Model Output Parsing:** The code assumes a certain output format from the Gemini model. You need to carefully inspect the actual output format and adjust the parsing logic in `llm_service.py` accordingly to reliably extract text descriptions and detected objects.
*   **AlloyDB Vector Search:** The `db/database.py` provides placeholder implementations for AlloyDB interaction. You'll need to implement actual vector similarity search using AlloyDB's capabilities or extensions.
*   **Frame Rectangles:** The current frontend code for `QueryResults.js` does not implement rendering rectangle marks on the images. You'll need to add logic to parse bounding box coordinates from the backend results and use a library (or canvas manipulation) to draw rectangles on the displayed frames.

This README provides a starting point. Deployment to Google Cloud and production readiness will require further in-depth configuration and testing.