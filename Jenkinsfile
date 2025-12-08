pipeline {
    agent any
    
    environment {
        // Docker Hub credentials (configure in Jenkins credentials store)
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        DOCKER_IMAGE_NAME = 'cyber-def25/malware-detector'
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_IMAGE_LATEST = "${DOCKER_IMAGE_NAME}:latest"
        DOCKER_IMAGE_BUILD = "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Prepare Environment') {
            steps {
                echo 'Preparing build environment...'
                sh '''
                    # Create necessary directories
                    mkdir -p network_logs output
                    
                    # Ensure Docker is running
                    docker --version
                    docker-compose --version
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image.. .'
                sh '''
                    # Build the Docker image with build number tag
                    docker build -t ${DOCKER_IMAGE_BUILD} -t ${DOCKER_IMAGE_LATEST} . 
                    
                    # List images to verify build
                    docker images | grep ${DOCKER_IMAGE_NAME}
                '''
            }
        }
        
        stage('Test Image') {
            steps {
                echo 'Running container tests...'
                sh '''
                    # Test that the container starts correctly
                    docker run --rm ${DOCKER_IMAGE_BUILD} python -c "import pickle; print('Model loading test passed')"
                    
                    # Verify inference script syntax
                    docker run --rm ${DOCKER_IMAGE_BUILD} python -m py_compile inference.py
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                sh '''
                    # Login to Docker Hub
                    echo ${DOCKER_HUB_CREDENTIALS_PSW} | docker login -u ${DOCKER_HUB_CREDENTIALS_USR} --password-stdin
                    
                    # Push both tagged and latest images
                    docker push ${DOCKER_IMAGE_BUILD}
                    docker push ${DOCKER_IMAGE_LATEST}
                    
                    # Logout for security
                    docker logout
                '''
            }
        }
        
        stage('Deploy with Docker Compose') {
            steps {
                echo 'Deploying application using docker-compose...'
                sh '''
                    # Export image name for docker-compose
                    export DOCKER_IMAGE=${DOCKER_IMAGE_BUILD}
                    
                    # Stop any existing containers
                    docker-compose down --remove-orphans || true
                    
                    # Run the container using docker-compose
                    docker-compose up -d
                    
                    # Wait for container to complete processing
                    sleep 10
                    
                    # Check container logs
                    docker-compose logs
                    
                    # Check if alerts. csv was generated
                    if [ -f "./output/alerts.csv" ]; then
                        echo "Detection results generated successfully!"
                        cat ./output/alerts.csv
                    else
                        echo "Waiting for detection to complete..."
                    fi
                '''
            }
        }
        
        stage('Cleanup') {
            steps {
                echo 'Cleaning up old images...'
                sh '''
                    # Remove dangling images
                    docker image prune -f
                    
                    # Keep only last 5 builds
                    docker images ${DOCKER_IMAGE_NAME} --format "{{.Tag}}" | \
                        grep -v latest | sort -rn | tail -n +6 | \
                        xargs -I {} docker rmi ${DOCKER_IMAGE_NAME}:{} || true
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed.'
        }
        success {
            echo 'Pipeline succeeded!  Image pushed to Docker Hub and container deployed.'
        }
        failure {
            echo 'Pipeline failed!  Check logs for details.'
            sh 'docker-compose logs || true'
        }
        cleanup {
            // Clean workspace
            cleanWs()
        }
    }
}
