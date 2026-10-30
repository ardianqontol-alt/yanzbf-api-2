#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
#  YANZBF AUTO-DEPLOYER - VERCEL API GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

G='\033[0;32m'; R='\033[0;31m'; Y='\033[1;33m'; C='\033[0;36m'; M='\033[0;35m'; NC='\033[0m'

clear
echo -e "${C}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${C}║           ${M}YANZBF AUTO-DEPLOYER - VERCEL API${C}               ║${NC}"
echo -e "${C}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Input Konfigurasi
read -p "$(echo -e "${Y}➜ Masukkan GitHub Token (ghp_...): ${NC}")" GITHUB_TOKEN
read -p "$(echo -e "${Y}➜ Masukkan Username GitHub lu: ${NC}")" GITHUB_USER
read -p "$(echo -e "${Y}➜ Masukkan Vercel Token: ${NC}")" VERCEL_TOKEN
echo ""
read -p "$(echo -e "${Y}➜ Mau bikin berapa API? (contoh 10 / 50): ${NC}")" JUMLAH_API

if [[ ! "$JUMLAH_API" =~ ^[0-9]+$ ]] || [ "$JUMLAH_API" -eq 0 ]; then
    echo -e "${R}✗ Jumlah API harus berupa angka dan lebih dari 0!${NC}"
    exit 1
fi

PREFIX="yanzbf-api"
PROJECT_DIR=$(pwd)
OUTPUT_FILE="$PROJECT_DIR/configapis.json"

# 2. Cek File Kode API
if [ ! -f "$PROJECT_DIR/vercel.json" ] || [ ! -d "$PROJECT_DIR/api" ]; then
    echo -e "\n${R}✗ File vercel.json / folder api/ tidak ditemukan di folder ini!${NC}"
    echo -e "${Y}Pastikan lu menjalankan script ini di dalam folder HEX yang ada api/, lib/, requirements.txt, dan vercel.json.${NC}"
    exit 1
fi

# Init git lokal
git init -q
git add . -A
git commit -q -m "YANZBF API Init"

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${G}✓ Mulai deploy ${JUMLAH_API} API...${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 3. Proses Deploy
echo "{" > "$OUTPUT_FILE"
SUKSES=0

for ((i=1; i<=JUMLAH_API; i++)); do
    REPO="${PREFIX}-${i}"
    echo -e "${Y}[${i}/${JUMLAH_API}]${NC} Memproses ${C}${REPO}${NC}..."

    # Buat Repo di GitHub
    RESP=$(curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"name\":\"${REPO}\",\"private\":false,\"auto_init\":false}" \
        "https://api.github.com/user/repos")
    
    if echo "$RESP" | grep -q '"message": "Repository creation failed"'; then
        echo -e "  ${R}✗ Gagal bikin repo (mungkin sudah ada). Skip...${NC}"
        continue
    fi

    # Push kode
    git remote remove origin 2>/dev/null
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO}.git"
    git push -u origin main -q -f 2>/dev/null

    # Deploy Vercel
    sleep 1.5
    DPL_RES=$(curl -s -X POST \
        -H "Authorization: Bearer ${VERCEL_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${REPO}\",\"gitSource\":{\"type\":\"github\",\"repo\":\"${GITHUB_USER}/${REPO}\"}}" \
        "https://api.vercel.com/v13/deployments")

    if echo "$DPL_RES" | grep -q '"error"'; then
        echo -e "  ${R}✗ Gagal deploy ke Vercel (Cek limit project/token).${NC}"
    else
        LINK="https://${REPO}.vercel.app/api/xorav2"
        echo -e "  ${G}✓ Sukses: ${LINK}${NC}"
        
        # Simpan ke configapis.json
        if [ $SUKSES -gt 0 ]; then echo "," >> "$OUTPUT_FILE"; fi
        echo "  \"$((SUKSES+1))\": \"${LINK}\"" >> "$OUTPUT_FILE"
        SUKSES=$((SUKSES+1))
    fi
done

echo -e "\n}" >> "$OUTPUT_FILE"

# 4. Selesai
echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $SUKSES -gt 0 ]; then
    echo -e "${G}✓ Selesai! Berhasil deploy ${SUKSES} API.${NC}"
    echo -e "${Y}File configapis.json sudah otomatis dibuat di:${NC}"
    echo -e "${C}${OUTPUT_FILE}${NC}"
    echo -e "Tinggal copy folder configapis.json ke folder client v9.py lu."
else
    echo -e "${R}✗ Tidak ada API yang berhasil dibuat. Cek token & koneksi lu.${NC}"
    rm -f "$OUTPUT_FILE"
fi
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"