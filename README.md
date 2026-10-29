# 🛡️ RHEL Layer 7 Anti-DoS & Anti-DDoS Architecture

[![TEK-UP University](https://img.shields.io/badge/Institution-TEK-UP%20University-blue.svg)](https://tek-up.de/)
[![Cybersecurity Engineering](https://img.shields.io/badge/Specialty-Cybersecurity%20Engineering-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()

> **Projet de Fin d'Études / Universitaire (5SSIR-D)**  
> **Auteurs :** Emna Jlassi & Amani Aloui  
> **Établissement :** École Supérieure Privée de Technologie & Ingénierie (TEK-UP), Tunisie.

---

## 📖 1. Introduction et Contexte

Les attaques DDoS de couche 7 (applicative) visent l'épuisement des ressources des serveurs web (mémoire, connexions) en exploitant le protocole HTTP avec des requêtes en apparence légitimes[cite: 5]. Contrairement aux attaques volumétriques réseau (couches 3-4), elles sont particulièrement difficiles à détecter car le trafic malveillant se confond avec le trafic réel[cite: 5].

Ce projet étudie, conçoit et valide expérimentalement une architecture de défense en profondeur de niveau 7 sur une application web vulnérable conteneurisée (`OWASP Juice Shop`) sous **Red Hat Enterprise Linux (RHEL)**[cite: 5].

### Objectifs principaux :
* **Défense en profondeur :** Combiner plusieurs mécanismes de sécurité complémentaires[cite: 5].
* **Réaction automatisée :** Bannir dynamiquement les adresses IP malveillantes sans intervention humaine[cite: 5].
* **Supervision en temps réel :** Suivre l'état du système et l'impact des attaques via un tableau de bord Grafana[cite: 5].
* **Validation expérimentale :** Tester l'efficacité des protections face à des scénarios réels (Flood HTTP, Slowloris, Botnet)[cite: 5].

---

## 🏗️ 2. Architecture du Système (Défense en Profondeur)

L'architecture repose sur un pipeline de filtrage strict où chaque couche intercepte un type specific de menace avant qu'elle n'atteigne l'application backend.

```text
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
