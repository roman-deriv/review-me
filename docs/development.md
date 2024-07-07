Get your code reviewed by an LLM.

## Description

Currently, the script fetches the PR, goes file by file, and makes comments about each one.

- I'd like to get more granular and start commenting on individual changes within files as a next step.
- Eventually, I'd like to get an overall comment that encompasses all the changes to summarize the review.

## Run the Project with Docker

1. **Clone the Repository**:
   ```shell
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Build the Docker Image**:
   - Ensure you have Docker installed and running on your system.
   - Build the Docker image using the provided `Dockerfile`:
     ```shell
     docker build -t review-me .
     ```

3. **Create and Configure the Environment File**:
   - Copy the `.env.example` file to `.env` and fill in your credentials:
     ```shell
     cp .env.example .env
     ```
   - Make sure the `.env` file is in the same directory as the `Dockerfile`.

4. **Run the Docker Container**:
   - Run the Docker container with the created image:
     ```shell
     docker run --env-file .env review-me
     ```

## Run the Project Locally (macOS)

- **Clone the Repository**:
   ```shell
   git clone <repository-url>
   cd <repository-directory>
   ```
- Create virtual environment (optional, recommended)
  ```shell
  python -m venv .venv
  source .venv/bin/activate
  ```
- Install requirements
  ```shell
  pip install -r requirements.txt
  ```

- Copy the `.env.example` file to `.env` and fill in your credentials:
  ```shell
  cp .env.example .env
  ```

- Run the entrypoint script
  ```shell
  python main.py
  ```
  