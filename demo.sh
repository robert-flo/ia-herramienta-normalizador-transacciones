#!/usr/bin/env bash
# Script de demostración en vivo del Normalizador de Transacciones Multifuente
# Estudiante: Roberto Carlos Flores Quintanilla · Kodigo (AI For Devs Jr. 5)

set -e

AZUL='\033[1;34m'
VERDE='\033[1;32m'
AMARILLO='\033[1;33m'
RESET='\033[0m'

echo -e "${AZUL}======================================================================${RESET}"
echo -e "${AZUL}   DEMOSTRACIÓN EN VIVO: NORMALIZADOR DE TRANSACCIONES MULTIFUENTE   ${RESET}"
echo -e "${AZUL}   Estudiante: Roberto Carlos Flores Quintanilla (AI For Devs Jr. 5) ${RESET}"
echo -e "${AZUL}======================================================================${RESET}"
echo ""

echo -e "${AMARILLO}[1/4] Caso 1: Lote bien formado (pruebas/bien_formado.json)${RESET}"
echo -e "Contenido del archivo:"
cat pruebas/bien_formado.json
echo ""
echo -e "${VERDE}-> Ejecutando: python3 main.py pruebas/bien_formado.json${RESET}"
python3 main.py pruebas/bien_formado.json
echo ""

echo -e "${AMARILLO}[2/4] Caso 2: Lote con errores y casos borde (pruebas/con_errores.json)${RESET}"
echo -e "Contenido del archivo:"
cat pruebas/con_errores.json
echo ""
echo -e "${VERDE}-> Ejecutando: python3 main.py pruebas/con_errores.json${RESET}"
python3 main.py pruebas/con_errores.json
echo ""

echo -e "${AMARILLO}[3/4] Caso 3: Ejemplo directo del enunciado (pruebas/ejemplo_enunciado.json)${RESET}"
echo -e "Contenido del archivo:"
cat pruebas/ejemplo_enunciado.json
echo ""
echo -e "${VERDE}-> Ejecutando: python3 main.py pruebas/ejemplo_enunciado.json${RESET}"
python3 main.py pruebas/ejemplo_enunciado.json
echo ""

echo -e "${AMARILLO}[4/4] Suite de pruebas automatizadas E2E (tests/test_e2e.py)${RESET}"
echo -e "${VERDE}-> Ejecutando: python3 -m unittest tests.test_e2e -v${RESET}"
python3 -m unittest tests.test_e2e -v
echo ""
echo -e "${AZUL}======================================================================${RESET}"
echo -e "${VERDE}Demostración completada exitosamente.${RESET}"
echo -e "Web Interactiva: https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/"
echo -e "Repositorio:     https://github.com/robert-flo/ia-herramienta-normalizador-transacciones"
echo -e "${AZUL}======================================================================${RESET}"
