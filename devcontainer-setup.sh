#!/usr/bin/env bash
set -e

echo "1. Installing Trivy..."
apt-get update && apt-get install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb release main" | tee -a /etc/apt/sources.list.d/trivy.list
apt-get update && apt-get install -y trivy

echo "2. Installing Marp CLI & Python Dependencies..."
npm install -g @marp-team/marp-cli opencode-ai
pip install -r requirements.txt

echo "3. Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "4. Starting Ollama Background Service & Fetching Qwen Model..."
ollama serve > /dev/null 2>&1 &
sleep 5
ollama pull qwen2.5-coder:7b

echo "✅ Environment Ready!"