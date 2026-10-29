# 🛡️ RHEL Layer 7 Anti-DoS & Anti-DDoS Architecture

> **Projet Académique — Module Audit ISO 27001**
>
> **Réalisé par :** Emna Jlassi ([@emna378](https://github.com/emna378))
>
> **Établissement :** École Supérieure Privée de Technologie & Ingénierie (TEK-UP), Tunisie

## 📖 1. Introduction et Contexte

Les attaques DDoS de couche 7 (applicative) visent l'épuisement des ressources des serveurs web (mémoire, connexions) en exploitant le protocole HTTP avec des requêtes en apparence légitimes. Contrairement aux attaques volumétriques réseau (couches 3-4), elles sont particulièrement difficiles à détecter car le trafic malveillant se confond avec le trafic réel.

Ce projet étudie, conçoit et valide expérimentalement une architecture de défense en profondeur de niveau 7 sur une application web vulnérable conteneurisée (`OWASP Juice Shop`) sous **Red Hat Enterprise Linux (RHEL)**.

### Objectifs principaux :

* **Défense en profondeur :** Combiner plusieurs mécanismes de sécurité complémentaires.

* **Réaction automatisée :** Bannir dynamiquement les adresses IP malveillantes sans intervention humaine.

* **Supervision en temps réel :** Suivre l'état du système et l'impact des attaques via un tableau de bord Grafana.

* **Validation expérimentale :** Tester l'efficacité des protections face à des scénarios réels (Flood HTTP, Slowloris, Botnet).

## 🏗️ 2. Architecture du Système (Défense en Profondeur)

L'architecture repose sur un pipeline de filtrage strict où chaque couche intercepte un type spécifique de menace avant qu'elle n'atteigne l'application backend.

```
[ Zone d'Attaque (Locust / Slowhttptest / PowerShell) ]
                       │
                       ▼
[ Reverse Proxy / WAF : Nginx + ModSecurity & OWASP CRS ] ──(Filtre signatures & Rate Limit)
                       │
                       ▼
[ Détection & Bannissement : Fail2ban (Jail HTTP 429 -> iptables DOCKER-USER) ]
                       │
                       ▼
[ Application Cible : OWASP Juice Shop (Isolée sur réseau Docker interne) ]
                       │
                       ▼
[ Stockage & Monitoring : Prometheus & Grafana (Dashboard centralisé) ]

```

## ⚙️ 3. Composants et Mécanismes de Sécurité

1. **Reverse Proxy & Rate Limiting (Nginx) :**

   * Limitation par IP (`limit_req` à $10\text{ req/s}$) et connexions simultanées (`limit_conn` à $20\text{ connexions/IP}$).

   * Limitation globale agrégée (`server_name` à $200\text{ req/s}$) pour contrer les attaques distribuées (Botnets).

   * Durcissement des timeouts (`client_header_timeout`, `client_body_timeout`, `send_timeout` réduits à **10 secondes**) pour étouffer les attaques lentes de type Slowloris.

2. **WAF & Filtrage Applicatif (ModSecurity & OWASP CRS 4.29) :**

   * Blocage immédiat (HTTP `403 Forbidden`) des outils d'attaque non dissimulés (Locust, Python-requests, ApacheBench, SQLMap, LOIC) via des règles personnalisées (`antiddos.conf`).

3. **Détection & Répression Réseau (Fail2ban) :**

   * Surveillance des journaux Nginx : déclenchement d'un ban réseau de 10 minutes (`bantime = 600s`) dès l'accumulation de 50 erreurs HTTP 429.

   * Intégration Docker : injection directe des règles de bannissement dans la chaîne `DOCKER-USER` d'iptables.

4. **Supervision (Prometheus & Grafana) :**

   * Collecte via 4 exportateurs (nginx-exporter, nginxlog-exporter, node_exporter, prometheus).

   * Tableau de bord regroupant l'état des connexions actives, le taux de blocage, les codes HTTP ($403$, $429$, $408$) et le compteur d'IP bannies.

## 🧪 4. Scénarios de Test et Résultats

Le système a été validé à travers 4 scénarios d'attaque distincts :

| Scénario | Outil / Méthode | Mécanisme de Défense Déclenché | Code HTTP / Résultat | 
| ----- | ----- | ----- | ----- | 
| **Test 1 :** Flood applicatif | **Locust** (User-Agent par défaut) | WAF ModSecurity (Règle 10001) | `403 Forbidden` (Rejet immédiat en amont) | 
| **Test 2 :** Flood HTTP rapide | **PowerShell** (User-Agent neutre) | Nginx Rate Limiting + Fail2ban | `429 Too Many Requests` puis **Bannissement iptables** | 
| **Test 3 :** Attaque lente (Slow DoS) | **Slowhttptest** (Slowloris) | Durcissement des Timeouts Nginx | `408 Request Timeout` (Fermeture des sockets inactifs) | 
| **Test 4 :** Simulation Botnet | Requêtes multi-sources simultanées | Limite globale agrégée Nginx (`global_limit`) | Régulation globale du trafic à $200\text{ req/s}$ | 

## 🚀 5. Guide de Déploiement Rapide

### 5.1. Prérequis Système
* **Système d'exploitation :** Red Hat Enterprise Linux (RHEL 8/9) ou compatible (Rocky Linux, AlmaLinux).
* **Dépendances système :** `git`, `iptables`, `fail2ban`.
* **Moteur de conteneurisation :** Docker Engine v20.10+ et Docker Compose v2+.

### 5.2. Installation des dépendances (RHEL)
```bash
# Mise à jour du système et installation des outils réseau
sudo dnf update -y
sudo dnf install -y git iptables fail2ban

# Démarrage des services nécessaires
sudo systemctl enable --now docker
sudo systemctl enable --now fail2ban
```

### 5.3. Déploiement de la Stack

1. **Cloner le dépôt GitHub :**
   ```bash
   git clone https://github.com/emna378/rhel-antiddos-project.git
   cd rhel-antiddos-project
   ```

2. **Créer le dossier de logs partagé pour Nginx et Fail2ban :**
   ```bash
   mkdir -p nginx/logs
   ```

3. **Lancer l'ensemble de la stack conteneurisée :**
   ```bash
   docker compose up -d
   ```

4. **Vérifier l'état d'exécution des conteneurs :**
   ```bash
   docker compose ps
   ```

### 5.4. Points d'accès aux services

| Service | Port local / URL | Description |
| :--- | :--- | :--- |
| **Reverse Proxy / Application** | `http://localhost:80` ou `https://localhost:443` | Point d'entrée protégé (ModSecurity + Nginx) |
| **Grafana Monitoring** | `http://localhost:3000` | Tableau de bord visuel en temps réel |
| **Prometheus** | `http://localhost:9092` | Serveur de collecte de métriques |
| **Nginx Log Exporter** | `http://localhost:4040/metrics` | Métriques d'analyse de logs HTTP |
| **Nginx Exporter** | `http://localhost:9113/metrics` | Métriques d'état Nginx |

### 5.5. Exécution rapide d'un test de validation
Pour tester immédiatement la protection WAF Layer 7 :
```bash
# Simuler une attaque de flood avec un User-Agent bloqué
curl -A "locust" -I http://localhost/
```
*Résultat attendu :* `HTTP/1.1 403 Forbidden` (bloqué par la règle ModSecurity 10001).

## 📜 6. Auteur

Projet individuel réalisé dans le cadre de la validation du module **Audit ISO 27001** à l' **Université TEK-UP**.

* **Emna Jlassi** — [GitHub (@emna378)](https://github.com/emna378) | [Email](mailto:emnajlassi234@gmail.com)
