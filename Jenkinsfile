pipeline {
    agent any

    environment {
        IMAGE_NAME    = "weatherops"
        IMAGE_TAG     = "${BUILD_NUMBER}"
        CONTAINER_APP = "weatherops_app"
        CONTAINER_NGX = "weatherops_nginx"
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

<<<<<<< HEAD
        stage('Checkout') {
=======
        // ─── 1. CHECKOUT ───────────────────────────────────────────
        stage('📥 Checkout') {
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
            steps {
                echo '=== Récupération du code source ==='
                checkout scm
                sh 'echo "Branche : $(git branch --show-current)" || true'
                sh 'echo "Commit  : $(git rev-parse --short HEAD)" || true'
            }
        }

<<<<<<< HEAD
        stage('Lint') {
=======
        // ─── 2. LINT & SYNTAX CHECK ────────────────────────────────
        stage('🔍 Lint') {
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
            steps {
                echo '=== Vérification syntaxe Python ==='
                sh '''
                    python3 -m py_compile app/main.py
                    python3 -m py_compile app/database.py
                    python3 -m py_compile app/routers/weather.py
                    python3 -m py_compile app/routers/alerts.py
                    python3 -m py_compile app/routers/cities.py
                    python3 -m py_compile app/services/weather_service.py
<<<<<<< HEAD
                    python3 -m py_compile app/services/alert_service.py
                    echo "Syntaxe Python correcte"
=======
                    echo "✔ Syntaxe Python correcte"
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                '''
            }
        }

<<<<<<< HEAD
        stage('Tests') {
            steps {
                echo '=== Exécution des tests ==='
                sh '''
                    pip install --quiet pytest pytest-asyncio httpx aiosqlite fastapi uvicorn jinja2 pydantic python-multipart python-dotenv
                    export DB_PATH=/tmp/test_jenkins_${BUILD_NUMBER}.db
                    export PYTHONPATH=${WORKSPACE}
                    python3 -m pytest tests/test_app.py -v --tb=short || true
=======
        // ─── 3. TESTS AUTOMATISÉS ──────────────────────────────────
        stage('🧪 Tests') {
            steps {
                echo '=== Exécution des tests automatisés ==='
                sh '''
                    pip install --quiet pytest pytest-asyncio httpx aiosqlite fastapi uvicorn jinja2 pydantic python-multipart python-dotenv
                    DB_PATH=/tmp/test_jenkins_$BUILD_NUMBER.db \
                        python3 -m pytest tests/test_app.py -v --tb=short 2>&1 | tee test_results.txt
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                '''
            }
            post {
                always {
                    sh 'rm -f /tmp/test_jenkins_*.db || true'
                }
            }
        }

<<<<<<< HEAD
        stage('Build Docker') {
            steps {
                echo '=== Construction de l image Docker ==='
                sh '''
                    docker build \
                        --no-cache \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                    echo "Image ${IMAGE_NAME}:${IMAGE_TAG} construite"
=======
        // ─── 4. BUILD DOCKER ───────────────────────────────────────
        stage('🐳 Build Docker') {
            steps {
                echo '=== Construction de l\'image Docker ==='
                sh '''
                    docker build \
                        --no-cache \
                        --target runtime \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                    echo "✔ Image ${IMAGE_NAME}:${IMAGE_TAG} construite"
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                    docker images ${IMAGE_NAME}
                '''
            }
        }

<<<<<<< HEAD
        stage('Deploy') {
            steps {
                echo '=== Déploiement ==='
                sh '''
                    [ -f .env ] || cp .env.example .env
                    docker compose down --remove-orphans || true
                    docker compose up -d weatherops nginx
                    sleep 10
=======
        // ─── 5. DEPLOY ─────────────────────────────────────────────
        stage('🚀 Deploy') {
            steps {
                echo '=== Déploiement des conteneurs ==='
                sh '''
                    # Copier .env si absent
                    [ -f .env ] || cp .env.example .env

                    # Arrêt des anciens conteneurs
                    docker compose down --remove-orphans || true

                    # Démarrage
                    docker compose up -d --build

                    # Attente démarrage
                    sleep 10
                    echo "✔ Conteneurs démarrés"
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                    docker compose ps
                '''
            }
        }

<<<<<<< HEAD
        stage('Health Check') {
            steps {
                echo '=== Vérification de santé ==='
=======
        // ─── 6. HEALTH CHECK ───────────────────────────────────────
        stage('❤️ Health Check') {
            steps {
                echo '=== Vérification de santé post-déploiement ==='
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                sh '''
                    MAX=10; I=0
                    until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
                        I=$((I+1))
<<<<<<< HEAD
                        [ $I -ge $MAX ] && echo "TIMEOUT" && exit 1
                        echo "Attente... ($I/$MAX)"
                        sleep 3
                    done
                    echo "API operationnelle"
                    curl -s http://localhost:8000/health
=======
                        [ $I -ge $MAX ] && echo "TIMEOUT health check" && exit 1
                        echo "Attente... ($I/$MAX)"
                        sleep 3
                    done
                    echo "✔ API opérationnelle"
                    curl -s http://localhost:8000/health | python3 -m json.tool
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
                '''
            }
        }
    }

<<<<<<< HEAD
    post {
        success {
            echo "BUILD #${BUILD_NUMBER} REUSSI - http://localhost"
        }
        failure {
            echo "BUILD #${BUILD_NUMBER} ECHOUE"
            sh 'docker compose logs --tail=20 weatherops || true'
=======
    // ─── POST-BUILD ────────────────────────────────────────────────
    post {
        success {
            echo """
╔══════════════════════════════════════╗
║  ✅  BUILD #${BUILD_NUMBER} RÉUSSI   ║
║  🌍  http://localhost                ║
║  📖  http://localhost:8000/docs      ║
╚══════════════════════════════════════╝
"""
        }
        failure {
            echo "❌ BUILD #${BUILD_NUMBER} ÉCHOUÉ — Consultez les logs"
            sh 'docker compose logs --tail=30 weatherops || true'
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
        }
        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
