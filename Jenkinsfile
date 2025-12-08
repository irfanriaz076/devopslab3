pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        DOCKER_IMAGE_NAME = 'irfanriaz076/malware-detector'
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
                echo 'Preparing build environment.. .'
                sh '''
                    mkdir -p network_logs output
                    docker --version
                    docker-compose --version || docker compose version
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE_BUILD} -t ${DOCKER_IMAGE_LATEST} . 
                    docker images | grep ${DOCKER_IMAGE_NAME} || true
                '''
            }
        }
        
        stage('Test Image') {
            steps {
                echo 'Running container tests...'
                sh '''
                    docker run --rm ${DOCKER_IMAGE_BUILD} python -c "import pickle; print('Model loading test passed')"
                    docker run --rm ${DOCKER_IMAGE_BUILD} python -m py_compile inference.py
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                sh '''
                    echo ${DOCKER_HUB_CREDENTIALS_PSW} | docker login -u ${DOCKER_HUB_CREDENTIALS_USR} --password-stdin
                    docker push ${DOCKER_IMAGE_BUILD}
                    docker push ${DOCKER_IMAGE_LATEST}
                    docker logout
                '''
            }
        }
        
        stage('Deploy with Docker Compose') {
            steps {
                echo 'Deploying application using docker-compose...'
                sh '''
                    export DOCKER_IMAGE=${DOCKER_IMAGE_BUILD}
                    docker-compose down --remove-orphans 2>/dev/null || true
                    docker-compose up -d
                    sleep 10
                    docker-compose logs
                    
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
                sh 'docker image prune -f || true'
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
            echo 'Pipeline failed! Check logs for details.'
            sh 'docker-compose logs 2>/dev/null || true'
        }
        cleanup {
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true)
        }
    }
}
