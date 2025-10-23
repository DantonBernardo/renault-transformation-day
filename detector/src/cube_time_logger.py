import json
import os
import requests
import threading
import time
from datetime import datetime
from collections import defaultdict

class CubeTimeLogger:
    def __init__(self):
        """Inicializa o logger de tempos dos cubos"""
        # Mapeamento de cores para faces do cubo mágico
        self.color_mapping = {
            'white': 'Frente',
            'yellow': 'Atras', 
            'red': 'Encima',
            'orange': 'Embaixo',
            'blue': 'Direita',
            'green': 'Esquerda'
        }
        
        # Sistema de grupos de 3 cubos
        self.current_group = []  # Grupo atual sendo formado
        self.group_number = 1
        self.all_groups = []  # Todos os grupos finalizados
        
        # Arquivo de log
        self.log_file = f"cube_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.json_file = f"cube_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Logger de tempos iniciado silenciosamente
        
        # Fila para requisições assíncronas
        self.request_queue = []
        self.is_sending = False
        
        # Configuração para envio de API
        self.enable_api_send = True  # Mude para False para desabilitar envio
    
    def send_to_api_async(self, payload):
        """Envia dados para API de forma assíncrona ultra-rápida"""
        def send_request():
            try:
                # Timeout reduzido para 2 segundos (mais rápido)
                response = requests.post("http://127.0.0.1:8000/api/groups", 
                                       json=payload, 
                                       timeout=2,  # Timeout reduzido
                                       headers={'Content-Type': 'application/json'})
                if response.status_code == 201:
                    print("✅ Grupo enviado com sucesso para a API!")
                else:
                    print(f"❌ Falha ao enviar grupo: {response.status_code}")
            except requests.exceptions.Timeout:
                print("⏰ Timeout ao enviar grupo para API (2s)")
            except requests.exceptions.ConnectionError:
                print("🔌 Erro de conexão com API - Laravel pode estar offline")
            except Exception as e:
                print(f"❌ Erro ao enviar grupo para API: {e}")
            finally:
                self.is_sending = False
        
        # Executa em thread separada para não travar a câmera
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()
    
    def add_cube(self, color, individual_time):
        """Adiciona um cubo ao grupo atual (apenas se a cor não existir no grupo)"""
        face_name = self.color_mapping.get(color, 'Desconhecida')
        
        # Verifica se a cor já existe no grupo atual
        existing_colors = [cube['color'] for cube in self.current_group]
        if color in existing_colors:
            return
        
        cube_data = {
            'color': color,
            'face_name': face_name,
            'individual_time': individual_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_group.append(cube_data)
        
        # Verifica se completou um grupo de 3 cores diferentes
        if len(self.current_group) == 3:
            self.finalize_group()
    
    def finalize_group(self):
        """Finaliza um grupo de 3 cubos com cores diferentes e calcula o tempo total"""
        # VALIDAÇÃO RIGOROSA: Só processa se tiver exatamente 3 cubos diferentes
        if len(self.current_group) != 3:
            print(f"⚠️ Grupo incompleto: {len(self.current_group)}/3 cubos")
            return

        colors = [cube['color'] for cube in self.current_group]
        if len(set(colors)) != 3:
            print(f"⚠️ Cores duplicadas detectadas: {colors}")
            return

        # Calcula tempo total do grupo
        group_total_time = sum(cube['individual_time'] for cube in self.current_group)
        
        print(f"🎯 GRUPO COMPLETO! Tempo total: {group_total_time:.2f}s")
        cubes_info = [f"{c['color']}({c['individual_time']:.1f}s)" for c in self.current_group]
        print(f"   Cubos: {cubes_info}")

        group_data = {
            'group_number': self.group_number,
            'cubes': self.current_group.copy(),
            'total_group_time': group_total_time,
            'timestamp': datetime.now().isoformat()
        }

        self.all_groups.append(group_data)
        self.save_to_files()
        self.analyze_delays()

        # ------------------------------
        # VALIDAÇÃO E ENVIO PARA API (ASSÍNCRONO)
        # ------------------------------
        
        # VALIDAÇÃO FINAL: Garante que temos exatamente 3 cubos válidos
        if len(self.current_group) != 3:
            print("❌ ERRO: Grupo não tem 3 cubos!")
            return
            
        # Valida cada cubo individualmente
        valid_cubes = []
        for cube in self.current_group:
            if (cube.get('color') and 
                cube.get('face_name') and 
                cube.get('individual_time', 0) > 0):
                valid_cubes.append(cube)
        
        if len(valid_cubes) != 3:
            print(f"❌ ERRO: Apenas {len(valid_cubes)}/3 cubos válidos!")
            return
        
        # Monta payload com validação
        payload = {
            "group_time": group_total_time,
            "cubes": [
                {
                    "color": cube["color"].upper(),
                    "face": cube["face_name"],
                    "individual_time": cube["individual_time"]
                } for cube in valid_cubes
            ]
        }
        
        print(f"📤 Enviando grupo #{self.group_number} para API...")
        print(f"   Tempo total: {group_total_time:.2f}s")

        # Envia de forma assíncrona para não travar a câmera (se habilitado)
        if self.enable_api_send:
            self.send_to_api_async(payload)
        else:
            print("📝 Envio para API desabilitado - dados salvos apenas localmente")

        self.current_group = []
        self.group_number += 1
    
    def save_to_files(self):
        """Salva os dados nos arquivos de texto e JSON"""
        # Salva em arquivo de texto simples
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=== RELATÓRIO DE TEMPOS DOS CUBOS ===\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            for group in self.all_groups:
                f.write(f"GRUPO {group['group_number']}:\n")
                f.write(f"Data/Hora: {group['timestamp']}\n")
                f.write("-" * 40 + "\n")
                
                for i, cube in enumerate(group['cubes'], 1):
                    f.write(f"{i}. Cor: {cube['color'].upper()}\n")
                    f.write(f"   Face: {cube['face_name']}\n")
                    f.write(f"   Tempo: {cube['individual_time']:.1f}s\n\n")
                
                f.write(f"TEMPO TOTAL DO GRUPO: {group['total_group_time']:.1f}s\n")
                f.write("=" * 50 + "\n\n")
        
        # Salva em arquivo JSON para dados estruturados
        json_data = {
            'session_start': datetime.now().isoformat(),
            'groups_of_three': self.all_groups,
            'total_groups': len(self.all_groups)
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def get_current_group_info(self):
        """Retorna informações do grupo atual"""
        existing_colors = [cube['color'] for cube in self.current_group]
        return {
            'current_group_size': len(self.current_group),
            'current_group': self.current_group.copy(),
            'current_colors': existing_colors,
            'total_groups': len(self.all_groups)
        }
    
    def force_finalize_group(self):
        """Força a finalização do grupo atual (mesmo que não tenha 3 cubos)"""
        if self.current_group:
            self.finalize_group()
    
    def toggle_api_send(self):
        """Alterna o envio para API (útil para debug)"""
        self.enable_api_send = not self.enable_api_send
        status = "habilitado" if self.enable_api_send else "desabilitado"
        print(f"🔄 Envio para API {status}")
    
    def get_summary(self):
        """Retorna um resumo dos dados"""
        total_cubes = sum(len(group['cubes']) for group in self.all_groups)
        total_time = sum(group['total_group_time'] for group in self.all_groups)
        
        return {
            'total_groups': len(self.all_groups),
            'total_cubes': total_cubes,
            'total_time': total_time,
            'current_group_size': len(self.current_group)
        }

# Função para usar o logger no webcam_detect_adaptive.py

  # -------------------------------
    # ANÁLISE DE DESEMPENHO E ATRASOS
    # -------------------------------
    def analyze_delays(self):
        """
        Analisa o último grupo comparando com a média esperada:
        - Tempo médio por cubo: 5s
        - Tempo médio total: 15s
        Detecta cubos ou grupos adiantados/atrasados em ±5s
        """
        if not self.all_groups:
            return

        expected_cube_time = 5.0       # tempo esperado por cubo (s)
        expected_group_time = 15.0     # tempo esperado por grupo (s)
        tolerance = 5.0                # margem de tolerância (s)

        last_group = self.all_groups[-1]
        total_time = last_group["total_group_time"]

        print("\n=== ANÁLISE DE DESEMPENHO ===")
        print(f"Grupo {last_group['group_number']} - Tempo total: {total_time:.2f}s\n")

        atraso_cubos = []
        adiantados_cubos = []

        # Analisa cubo por cubo
        for cube in last_group["cubes"]:
            tempo = cube["individual_time"]
            cor = cube["color"]
            diferenca = tempo - expected_cube_time
            

            if diferenca > tolerance:
                atraso_cubos.append((cor, tempo, diferenca))
            elif diferenca < -tolerance:
                adiantados_cubos.append((cor, tempo, diferenca))

            print(f"- {cor.upper()}: {tempo:.2f}s (diferença: {diferenca:+.2f}s)")

        # Análise do grupo total
        total_diff = total_time - expected_group_time
        print("\nTempo total esperado: 15.00s")
        print(f"Desvio total do grupo: {total_diff:+.2f}s")

        # Diagnóstico geral
        if total_diff > tolerance:
            print("🚨 O grupo atrasou em relação ao tempo médio!")
            if atraso_cubos:
                print("Causado por:")
                for cor, tempo, dif in atraso_cubos:
                    print(f"  -> {cor.upper()} demorou {dif:+.2f}s a mais ({tempo:.2f}s)")
        elif total_diff < -tolerance:
            print("⚡ O grupo foi mais rápido que o esperado!")
            if adiantados_cubos:
                print("Provavelmente acelerado por:")
                for cor, tempo, dif in adiantados_cubos:
                    print(f"  -> {cor.upper()} foi {dif:+.2f}s mais rápido ({tempo:.2f}s)")
        else:
            print("✅ O grupo está dentro do tempo esperado.")

        print("=" * 50)

def create_logger():
    """Cria uma instância do logger para usar no detector principal"""
    return CubeTimeLogger()

# Exemplo de uso no webcam_detect_adaptive.py:
"""
# No início do arquivo webcam_detect_adaptive.py, adicione:
from cube_time_logger import create_logger

# Na função main(), após criar o detector:
logger = create_logger()

# Quando um cubo sair (na função update_tracking), adicione:
logger.add_cube(color, total_time)

# Para finalizar grupo manualmente, adicione no controle de teclas:
elif key == ord('f'):  # Tecla 'f' para finalizar grupo
    logger.force_finalize_group()
"""
