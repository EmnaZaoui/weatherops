pipeline {
    agent any

    environment {
        IMAGE_NAME    = "weatherops"
        IMAGE_TAG     = "${BUILD_NUMBER}"
        CONTAINER_APP = "weatherops_app"
        CONTAINER_NGX = "weatherops_nginx"
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
                sh 'echo "Branche : $(git branch --show-current)" || true'
                sh 'echo "Commit  : $(git rev-parse --short HEAD)" || true'
            }
        }

        stage('Lint') {
            steps {
                echo '=== Vérification syntaxe Python ==='
                sh '''
                    python3 -m py_compile app/main.py
                    python3 -m py_compile app/database.py
                    python3 -m py_compile app/routers/weather.py
                    python3 -m py_compile app/routers/alerts.py
                    python3 -m py_compile app/routers/cities.py
                    python3 -m py_compile app/services/weather_service.py
                    python3 -m py_compile app/services/alert_service.py
                    echo "Syntaxe Python correcte"
                '''
            }
        }

        stage('Tests') {
            steps {
                echo '=== Exécution des tests ==='
                sh '''
                    pip install --quiet pytest pytest-asyncio httpx aiosqlite fastapi uvicorn jinja2 pydantic python-multipart python-dotenv
                    export DB_PATH=/tmp/test_jenkins_${BUILD_NUMBER}.db
                    export PYTHONPATH=${WORKSPACE}
                    python3 -m pytest tests/test_app.py -v --tb=short || true
                '''
            }
            post {
                always {
                    sh 'rm -f /tmp/test_jenkins_*.db || true'
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo '=== Construction de l image Docker ==='
                sh '''
                    docker build \
                        --no-cache \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                    echo "Image construite"
                    docker images ${IMAGE_NAME}
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Déploiement ==='
                sh '''
                    [ -f .env ] || cp .env.example .env
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
                    echo "API operationnelle"
                    curl -s http://localhost:8000/health
                '''
            }
        }
    }

    post {
        success {
            echo "BUILD #${BUILD_NUMBER} REUSSI - http://localhost"
        }
        failure {
            echo "BUILD #${BUILD_NUMBER} ECHOUE"
            sh 'docker compose logs --tail=20 weatherops || true'
        }
        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}