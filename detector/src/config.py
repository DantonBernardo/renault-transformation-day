"""
Configurações gerais do sistema de detecção de cubos
Altere estes valores para ajustar os tempos médios esperados
"""

# ===========================================
# CONFIGURAÇÕES DE TEMPO MÉDIO
# ===========================================

# Tempo médio esperado por cubo individual (em segundos)
EXPECTED_CUBE_TIME = 5.0

# Tempo médio esperado por grupo (sempre 3x o tempo individual)
EXPECTED_GROUP_TIME = EXPECTED_CUBE_TIME * 3  # 15.0s

# Margem de tolerância para análise de desempenho (em segundos)
TOLERANCE = 5.0

# ===========================================
# CONFIGURAÇÕES DO SERVIDOR
# ===========================================

# Limite para considerar grupo atrasado (em segundos)
# Deve ser menor que EXPECTED_GROUP_TIME + TOLERANCE
DELAYED_GROUP_THRESHOLD = 10.0

# Limite para considerar grupo adiantado (em segundos)  
# Deve ser maior que EXPECTED_GROUP_TIME - TOLERANCE
EARLY_GROUP_THRESHOLD = 2.0

# ===========================================
# CONFIGURAÇÕES DE DETECÇÃO
# ===========================================

# Configurações do detector de cores
COLOR_CONFIDENCE_THRESHOLD = 0.05
MAX_DISTANCE_THRESHOLD = 150
MAX_CUBES_SIMULTANEOUS = 6
MIN_STABILITY_FRAMES = 5
MIN_DETECTION_DURATION = 0.2
MIN_CONSECUTIVE_FRAMES = 6
MAX_MISSED_FRAMES = 2
COOLDOWN_DURATION = 2.0
MIN_EXIT_FRAMES = 10

# ===========================================
# CONFIGURAÇÕES DE API
# ===========================================

# URL base da API (ajuste conforme necessário)
API_BASE_URL = "http://127.0.0.1:8000/api"

# ===========================================
# VALIDAÇÕES
# ===========================================

# Valida se as configurações fazem sentido
def validate_config():
    """Valida se as configurações estão consistentes"""
    if DELAYED_GROUP_THRESHOLD >= EXPECTED_GROUP_TIME + TOLERANCE:
        print(f"⚠️ AVISO: DELAYED_GROUP_THRESHOLD ({DELAYED_GROUP_THRESHOLD}s) deveria ser menor que EXPECTED_GROUP_TIME + TOLERANCE ({EXPECTED_GROUP_TIME + TOLERANCE}s)")
    
    if EARLY_GROUP_THRESHOLD <= EXPECTED_GROUP_TIME - TOLERANCE:
        print(f"⚠️ AVISO: EARLY_GROUP_THRESHOLD ({EARLY_GROUP_THRESHOLD}s) deveria ser maior que EXPECTED_GROUP_TIME - TOLERANCE ({EXPECTED_GROUP_TIME - TOLERANCE}s)")
    
    if EXPECTED_GROUP_TIME != EXPECTED_CUBE_TIME * 3:
        print(f"⚠️ AVISO: EXPECTED_GROUP_TIME ({EXPECTED_GROUP_TIME}s) deveria ser 3x EXPECTED_CUBE_TIME ({EXPECTED_CUBE_TIME * 3}s)")

# Executa validação ao importar o módulo
if __name__ == "__main__":
    validate_config()
else:
    validate_config()
