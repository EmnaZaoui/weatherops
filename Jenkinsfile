pipeline {
    agent any

    environment {
        IMAGE_NAME = "weatherops"
        IMAGE_TAG  = "${BUILD_NUMBER}"
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Récupération du code source ==='
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                echo '=== Vérification syntaxe Python ==='
                sh '''
                    docker run --rm \
                        -v ${WORKSPACE}:/app \
                        -w /app \
                        python:3.11-slim \
                        python3 -m py_compile app/main.py
                    echo " Syntaxe Python correcte"
                '''
            }
        }

        stage('Tests') {
            steps {
                echo '=== Exécution des tests ==='
                sh '''
                    docker run --rm \
                        -v ${WORKSPACE}:/app \
                        -w /app \
                        -e DB_PATH=/tmp/test.db \
                        -e PYTHONPATH=/app \
                        python:3.11-slim \
                        sh -c "pip install -q pytest httpx aiosqlite fastapi uvicorn jinja2 pydantic python-multipart python-dotenv && pytest tests/test_app.py -v --tb=short"
                '''
            }
        }

        stage('Build Docker') {
            steps {
                echo '=== Construction image Docker ==='
                sh '''
                    docker build \
                        --no-cache \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                    echo " Image construite"
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Déploiement ==='
                sh '''
                    [ -f .env ] || touch .env
                    docker compose down --remove-orphans || true
                    docker compose up -d weatherops nginx
                    sleep 10
                    docker compose ps
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '=== Vérification de santé ==='
                sh '''
                    MAX=10; I=0
                    until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
                        I=$((I+1))
                        [ $I -ge $MAX ] && echo "TIMEOUT" && exit 1
                        echo "Attente... ($I/$MAX)"
                        sleep 3
                    done
                    echo " API opérationnelle"
                '''
            }
        }
    }

    post {
        success {
            echo " BUILD #${BUILD_NUMBER} REUSSI - http://localhost"
        }
        failure {
            echo " BUILD #${BUILD_NUMBER} ECHOUE"
        }
    }
}