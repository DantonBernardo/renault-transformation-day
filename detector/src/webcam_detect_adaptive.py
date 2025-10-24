import cv2
from ultralytics import YOLO
import numpy as np
import time
from collections import defaultdict
from cube_time_logger import create_logger
from config import (
    COLOR_CONFIDENCE_THRESHOLD, MAX_DISTANCE_THRESHOLD, MAX_CUBES_SIMULTANEOUS,
    MIN_STABILITY_FRAMES, MIN_DETECTION_DURATION, MIN_CONSECUTIVE_FRAMES,
    MAX_MISSED_FRAMES, COOLDOWN_DURATION, MIN_EXIT_FRAMES
)

class CubeDetector:
    def __init__(self, model_path):
        """Inicializa o detector de cubos com tracking por cor"""
        self.model = YOLO(model_path)
        self.confidence = 0.5
        
        # Mapeamento de cores para faces do cubo magico
        self.color_mapping = {
            'white': 'Frente',
            'yellow': 'Atras', 
            'red': 'Encima',
            'orange': 'Embaixo',
            'blue': 'Direita',
            'green': 'Esquerda'
        }
        
        # Ranges de cores em HSV com margens maiores para iluminação variável
        self.color_ranges = {
            'white': ([0, 0, 150], [180, 80, 255]),  # Margem maior para branco
            'yellow': ([15, 80, 80], [35, 255, 255]),  # Margem expandida
            'red': ([0, 80, 80], [15, 255, 255]),  # Margem expandida
            'red2': ([165, 80, 80], [180, 255, 255]),  # Margem expandida
            'orange': ([5, 80, 80], [25, 255, 255]),  # Margem expandida
            'blue': ([95, 60, 60], [135, 255, 255]),  # Margem muito maior para azul
            'green': ([35, 80, 80], [85, 255, 255])  # Margem expandida
        }
        
        # Sistema de tracking por cor - cada cor e um cubo diferente
        self.active_cubes_by_color = {}  # {color: cube_data}
        self.cube_history = []  # Historico de cubos que sairam
        self.color_total_times = defaultdict(float)  # Tempo total por cor
        
        # Parametros de tracking melhorados (usando configurações)
        self.max_distance_threshold = MAX_DISTANCE_THRESHOLD
        self.color_confidence_threshold = COLOR_CONFIDENCE_THRESHOLD
        self.max_cubes_simultaneous = MAX_CUBES_SIMULTANEOUS
        
        # Sistema de estabilizacao melhorado para evitar duplicatas
        self.color_detection_history = {}  # {color: [detected_colors_list]}
        self.cube_stability_frames = {}  # {color: frame_count}
        self.min_stability_frames = MIN_STABILITY_FRAMES
        
        # Parametros de estabilizacao
        self.min_color_samples = 2  # Reduzido para detecção mais rápida
        self.max_color_history = 6  # Reduzido para detecção mais rápida
        self.color_stability_threshold = 0.6  # 60% das deteccoes devem concordar
        
        # Sistema de cooldown para evitar detecções duplicadas
        self.color_cooldown = {}  # {color: last_detection_time}
        self.cooldown_duration = COOLDOWN_DURATION
        
        # Sistema de verificação de saída do cubo
        self.cube_exit_frames = {}  # {color: frames_sem_deteccao}
        self.min_exit_frames = MIN_EXIT_FRAMES
        
        # Sistema de debounce temporal - só considera cor após tempo configurado
        self.color_detection_start = {}  # {color: first_detection_time}
        self.min_detection_duration = MIN_DETECTION_DURATION
        self.color_detection_frames = {}  # {color: frames_consecutivos_detectados}
        self.min_consecutive_frames = MIN_CONSECUTIVE_FRAMES
        self.max_missed_frames = MAX_MISSED_FRAMES
        self.color_missed_frames = {}  # {color: frames_perdidos_consecutivos}
        
        # Debug - mostra informacoes de deteccao
        self.debug_mode = True
        
        # Modo de detecção rápida
        self.quick_detection_mode = False
        self.quick_detection_duration = 0.1  # 0.1 segundos para modo rápido
        self.quick_detection_frames = 3  # 3 frames para modo rápido
        
    def detect_cube_color(self, frame, bbox):
        """Detecta a cor dominante do cubo com filtros de ruído melhorados"""
        x1, y1, x2, y2 = bbox
        
        # Extrai região do cubo
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return 'unknown', 0.0
        
        # Aplica filtro gaussiano para reduzir ruído
        roi_blurred = cv2.GaussianBlur(roi, (5, 5), 0)
        
        # Converte para HSV
        hsv = cv2.cvtColor(roi_blurred, cv2.COLOR_BGR2HSV)
        
        # Pega região central (maior área para melhor análise)
        h, w = hsv.shape[:2]
        center_h, center_w = h // 2, w // 2
        center_size = min(h, w) // 2  # Aumentado para melhor detecção
        
        center_roi = hsv[
            max(0, center_h - center_size//2):min(h, center_h + center_size//2),
            max(0, center_w - center_size//2):min(w, center_w + center_size//2)
        ]
        
        if center_roi.size == 0:
            return 'unknown', 0.0
        
        # Aplica morfologia para limpar a máscara
        kernel = np.ones((3,3), np.uint8)
        
        # Testa cada cor com filtros melhorados
        color_scores = {}
        
        for color_name, (lower, upper) in self.color_ranges.items():
            if color_name == 'red2':
                continue
                
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            
            mask = cv2.inRange(center_roi, lower, upper)
            # Aplica operações morfológicas para limpar ruído
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            total_pixels = mask.size
            color_pixels = np.sum(mask > 0)
            percentage = color_pixels / total_pixels if total_pixels > 0 else 0
            
            color_scores[color_name] = percentage
        
        # Trata vermelho especial - combina dois ranges
        red_lower1 = np.array(self.color_ranges['red'][0], dtype=np.uint8)
        red_upper1 = np.array(self.color_ranges['red'][1], dtype=np.uint8)
        red_lower2 = np.array(self.color_ranges['red2'][0], dtype=np.uint8)
        red_upper2 = np.array(self.color_ranges['red2'][1], dtype=np.uint8)
        
        mask1 = cv2.inRange(center_roi, red_lower1, red_upper1)
        mask2 = cv2.inRange(center_roi, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        # Aplica morfologia também no vermelho
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        
        total_pixels = red_mask.size
        red_pixels = np.sum(red_mask > 0)
        color_scores['red'] = red_pixels / total_pixels if total_pixels > 0 else 0
        
        # Encontra melhor cor
        if not color_scores:
            return 'unknown', 0.0
        
        best_color = max(color_scores, key=color_scores.get)
        confidence = color_scores[best_color]
        
        # Debug - mostra informações de detecção (removido para limpar terminal)
        
        # Thresholds específicos por cor com margens maiores para iluminação variável
        color_thresholds = {
            'white': 0.015,  # Threshold ainda mais baixo para branco
            'blue': 0.02,    # Threshold reduzido para azul
            'red': 0.025,    # Threshold reduzido
            'orange': 0.025, # Threshold reduzido
            'yellow': 0.025, # Threshold reduzido
            'green': 0.025   # Threshold reduzido
        }
        
        min_threshold = color_thresholds.get(best_color, 0.05)
        
        if confidence < min_threshold:
            return 'unknown', confidence
        
        return best_color, confidence
    
    def test_color_ranges(self, frame, bbox):
        """Função de teste para analisar diferentes ranges de cores"""
        x1, y1, x2, y2 = bbox
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return
        
        roi_blurred = cv2.GaussianBlur(roi, (5, 5), 0)
        hsv = cv2.cvtColor(roi_blurred, cv2.COLOR_BGR2HSV)
        
        h, w = hsv.shape[:2]
        center_h, center_w = h // 2, w // 2
        center_size = min(h, w) // 2
        
        center_roi = hsv[
            max(0, center_h - center_size//2):min(h, center_h + center_size//2),
            max(0, center_w - center_size//2):min(w, center_w + center_size//2)
        ]
        
        if center_roi.size == 0:
            return
        
        # Testa ranges alternativos para azul e branco
        test_ranges = {
            'white_alt1': ([0, 0, 180], [180, 30, 255]),
            'white_alt2': ([0, 0, 200], [180, 50, 255]),
            'white_alt3': ([0, 0, 160], [180, 60, 255]),
            'blue_alt1': ([100, 60, 60], [130, 255, 255]),
            'blue_alt2': ([100, 80, 80], [130, 255, 255]),
            'blue_alt3': ([95, 50, 50], [135, 255, 255])
        }
        
        # Teste de ranges de cores (removido para limpar terminal)
        for name, (lower, upper) in test_ranges.items():
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(center_roi, lower, upper)
            total_pixels = mask.size
            color_pixels = np.sum(mask > 0)
            percentage = color_pixels / total_pixels if total_pixels > 0 else 0
    
    def draw_time_block(self, frame, detector):
        """Desenha um bloco visual destacado com os tempos totais por cor"""
        if not detector.color_total_times:
            return
        
        # Dimensões do bloco
        block_width = 300
        block_height = 200
        block_x = frame.shape[1] - block_width - 20  # 20px da borda direita
        block_y = 20  # 20px do topo
        
        # Desenha fundo do bloco com transparência
        overlay = frame.copy()
        cv2.rectangle(overlay, (block_x, block_y), (block_x + block_width, block_y + block_height), 
                     (0, 0, 0), -1)  # Fundo preto
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Borda do bloco
        cv2.rectangle(frame, (block_x, block_y), (block_x + block_width, block_y + block_height), 
                     (255, 255, 255), 2)
        
        # Título do bloco
        title_y = block_y + 25
        cv2.putText(frame, "TEMPOS TOTAIS POR COR", (block_x + 10, title_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Cores para cada linha
        color_colors = {
            'white': (255, 255, 255),
            'yellow': (0, 255, 255),
            'red': (0, 0, 255),
            'orange': (0, 165, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0)
        }
        
        # Desenha cada cor com seu tempo total
        y_offset = title_y + 30
        for color, total_time in detector.color_total_times.items():
            face_name = detector.color_mapping.get(color, 'Desconhecida')
            text = f"{color.upper()}: {total_time:.1f}s"
            
            # Cor do texto baseada na cor do cubo
            text_color = color_colors.get(color, (255, 255, 255))
            
            cv2.putText(frame, text, (block_x + 15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
            y_offset += 25
    
    def calculate_distance(self, bbox1, bbox2):
        """Calcula distância entre centroides de duas bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        center1 = ((x1_1 + x2_1) // 2, (y1_1 + y2_1) // 2)
        center2 = ((x1_2 + x2_2) // 2, (y1_2 + y2_2) // 2)
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def get_stable_color(self, cube_id):
        """Retorna a cor mais estável baseada no histórico melhorado"""
        if cube_id not in self.color_detection_history or len(self.color_detection_history[cube_id]) < self.min_color_samples:
            return 'unknown', 0.0
        
        # Conta frequência de cada cor no histórico
        color_counts = defaultdict(int)
        for detected_color in self.color_detection_history[cube_id]:
            color_counts[detected_color] += 1
        
        if not color_counts:
            return 'unknown', 0.0
        
        # Retorna a cor mais frequente
        most_common_color = max(color_counts, key=color_counts.get)
        confidence = color_counts[most_common_color] / len(self.color_detection_history[cube_id])
        
        # Só retorna a cor se a confiança for alta o suficiente E não estiver em cooldown
        current_time = time.time()
        if (confidence >= self.color_stability_threshold and 
            most_common_color not in self.color_cooldown or 
            current_time - self.color_cooldown.get(most_common_color, 0) > self.cooldown_duration):
            return most_common_color, confidence
        else:
            return 'unknown', confidence
    
    def is_color_in_cooldown(self, color):
        """Verifica se uma cor está em período de cooldown"""
        current_time = time.time()
        return (color in self.color_cooldown and 
                current_time - self.color_cooldown[color] < self.cooldown_duration)
    
    def update_tracking(self, detections, current_time):
        """Sistema de tracking baseado em cores com verificação robusta de saída"""
        # Marca todos os cubos ativos como não detectados neste frame
        for color in self.active_cubes_by_color:
            self.active_cubes_by_color[color]['detected_this_frame'] = False
        
        # Processa cada detecção
        for detection in detections:
            bbox = detection['bbox']
            
            # Detecta cor da detecção
            cube_color, color_conf = self.detect_cube_color(
                detection.get('frame', None), bbox
            )
            
            if (color_conf > self.color_confidence_threshold and 
                cube_color != 'unknown' and 
                not self.is_color_in_cooldown(cube_color)):
                
                # Verifica se já existe um cubo desta cor
                if cube_color in self.active_cubes_by_color:
                    # Atualiza cubo existente da mesma cor
                    cube = self.active_cubes_by_color[cube_color]
                    cube['bbox'] = bbox
                    cube['last_seen'] = current_time
                    cube['detected_this_frame'] = True
                    
                    # Reset contador de frames sem detecção
                    self.cube_exit_frames[cube_color] = 0
                    
                    # Adiciona cor detectada ao histórico
                    if cube_color not in self.color_detection_history:
                        self.color_detection_history[cube_color] = []
                    
                    self.color_detection_history[cube_color].append(cube_color)
                    
                    # Mantém apenas os últimos valores
                    if len(self.color_detection_history[cube_color]) > self.max_color_history:
                        self.color_detection_history[cube_color] = self.color_detection_history[cube_color][-self.max_color_history:]
                    
                else:
                    # Nova cor detectada - verifica se foi detectada por tempo suficiente
                    if cube_color not in self.color_detection_start:
                        # Primeira detecção desta cor
                        self.color_detection_start[cube_color] = current_time
                        self.color_detection_frames[cube_color] = 1
                        self.color_missed_frames[cube_color] = 0
                        print(f"🔍 Iniciando detecção de cor {cube_color}...")
                    else:
                        # Reset contador de frames perdidos (cor foi detectada novamente)
                        self.color_missed_frames[cube_color] = 0
                        
                        # Incrementa contador de frames detectados
                        self.color_detection_frames[cube_color] += 1
                        
                        # Verifica se passou do tempo mínimo de detecção
                        detection_duration = current_time - self.color_detection_start[cube_color]
                        
                        # Usa parâmetros do modo rápido se ativado
                        required_duration = self.quick_detection_duration if self.quick_detection_mode else self.min_detection_duration
                        required_frames = self.quick_detection_frames if self.quick_detection_mode else self.min_consecutive_frames
                        
                        if (detection_duration >= required_duration and 
                            self.color_detection_frames[cube_color] >= required_frames):
                            
                            # Cor confirmada após 0.5 segundos - cria novo cubo
                            # O entry_time deve ser o momento em que a detecção começou, não quando foi confirmada
                            detection_start_time = self.color_detection_start[cube_color]
                            cube_id = f"cubo_{cube_color}_{len(self.active_cubes_by_color) + 1}"
                            self.active_cubes_by_color[cube_color] = {
                                'id': cube_id,
                                'color': cube_color,
                                'entry_time': detection_start_time,  # Inclui o tempo de detecção
                                'last_seen': current_time,
                                'bbox': bbox,
                                'detected_this_frame': True
                            }
                            
                            # Inicializa histórico de cores e contador de saída
                            self.color_detection_history[cube_color] = [cube_color]
                            self.cube_exit_frames[cube_color] = 0
                            
                            # Limpa contadores de detecção
                            del self.color_detection_start[cube_color]
                            del self.color_detection_frames[cube_color]
                            if cube_color in self.color_missed_frames:
                                del self.color_missed_frames[cube_color]
                            
                            mode_text = "MODO RÁPIDO" if self.quick_detection_mode else "NORMAL"
                            print(f"✅ Cor {cube_color} confirmada após {detection_duration:.1f}s - Cubo adicionado ao grupo! ({mode_text})")
                        else:
                            # Ainda não passou do tempo mínimo - mostra progresso
                            progress = min(100, (detection_duration / required_duration) * 100)
                            mode_text = "RÁPIDO" if self.quick_detection_mode else "NORMAL"
                            print(f"⏳ Cor {cube_color}: {progress:.0f}% ({detection_duration:.1f}s/{required_duration:.1f}s) [{mode_text}]")
        
        # Limpa detecções que não foram confirmadas há muito tempo
        colors_to_clean = []
        for color in self.color_detection_start:
            if current_time - self.color_detection_start[color] > 3.0:  # 3 segundos sem confirmação
                colors_to_clean.append(color)
        
        for color in colors_to_clean:
            print(f"❌ Cor {color} descartada - não foi confirmada em 3 segundos")
            del self.color_detection_start[color]
            if color in self.color_detection_frames:
                del self.color_detection_frames[color]
        
        # Incrementa contadores de frames perdidos para cores em detecção
        colors_detected_this_frame = set()
        for detection in detections:
            cube_color, color_conf = self.detect_cube_color(
                detection.get('frame', None), detection['bbox']
            )
            if (color_conf > self.color_confidence_threshold and 
                cube_color != 'unknown' and 
                not self.is_color_in_cooldown(cube_color)):
                colors_detected_this_frame.add(cube_color)
        
        # Processa cores em detecção que não foram detectadas neste frame
        colors_to_reset = []
        for color in self.color_detection_start:
            if color not in colors_detected_this_frame:
                # Incrementa contador de frames perdidos
                if color not in self.color_missed_frames:
                    self.color_missed_frames[color] = 0
                self.color_missed_frames[color] += 1
                
                # Se perdeu muitos frames consecutivos, reseta a detecção
                if self.color_missed_frames[color] > self.max_missed_frames:
                    colors_to_reset.append(color)
                    print(f"🔄 Resetando detecção de cor {color} - {self.color_missed_frames[color]} frames perdidos")
                else:
                    print(f"⚠️ Cor {color}: {self.color_missed_frames[color]}/{self.max_missed_frames} frames perdidos")
        
        # Remove contadores de cores que perderam muitos frames
        for color in colors_to_reset:
            del self.color_detection_start[color]
            if color in self.color_detection_frames:
                del self.color_detection_frames[color]
            if color in self.color_missed_frames:
                del self.color_missed_frames[color]
        
        # Verifica cubos que não foram detectados neste frame
        cubes_to_remove = []
        for color, cube_data in self.active_cubes_by_color.items():
            if not cube_data['detected_this_frame']:
                # Incrementa contador de frames sem detecção
                if color not in self.cube_exit_frames:
                    self.cube_exit_frames[color] = 0
                self.cube_exit_frames[color] += 1
                
                # Só remove se passou do número mínimo de frames sem detecção
                if self.cube_exit_frames[color] >= self.min_exit_frames:
                    cubes_to_remove.append(color)
                    print(f"✅ Cubo {color} confirmado como saído após {self.cube_exit_frames[color]} frames sem detecção")
        
        # Remove cubos confirmados como saídos
        for color in cubes_to_remove:
            cube_data = self.active_cubes_by_color[color]
            # Usa o tempo da última detecção (mais preciso)
            total_time = cube_data['last_seen'] - cube_data['entry_time']
            
            # Adiciona ao tempo total desta cor
            self.color_total_times[color] += total_time
            
            cube_data['total_time'] = total_time
            cube_data['final_color'] = color
            cube_data['total_time_for_color'] = self.color_total_times[color]
            
            self.cube_history.append(cube_data.copy())
            
            # Adiciona ao logger se estiver disponível
            if hasattr(self, 'logger'):
                self.logger.add_cube(color, total_time)
            
            # Adiciona cooldown para evitar detecção duplicada
            self.color_cooldown[color] = current_time
            
            del self.active_cubes_by_color[color]
            # Limpa histórico de cores e contador de saída
            if color in self.color_detection_history:
                del self.color_detection_history[color]
            if color in self.cube_exit_frames:
                del self.cube_exit_frames[color]
    
    def detect_cubes(self, frame, current_time):
        """Detecta cubos no frame"""
        # Faz predição
        results = self.model(frame, conf=self.confidence, verbose=False)
        
        detections = []
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': conf,
                        'frame': frame  # Passa o frame para detecção de cor
                    })
        
        # Atualiza tracking
        self.update_tracking(detections, current_time)
        
        return detections

def main():
    print("[INFO] Iniciando script...")

    # Carrega o melhor modelo disponível
    model_paths = [
        "../runs-cube/yolov8n-cube5/weights/best.pt",
        "../runs-cube/yolov8n-cube4/weights/best.pt",
        "../runs-cube/yolov8n-cube3/weights/best.pt",
        "../runs-cube/yolov8n-cube2/weights/best.pt",
        "../runs-cube/yolov8n-cube/weights/best.pt"
    ]
    
    model_path = None
    for path in model_paths:
        try:
            YOLO(path)
            model_path = path
            print(f"[INFO] Modelo carregado: {path}")
            break
        except Exception as e:
            print(f"[WARN] Modelo {path} não pôde ser carregado: {e}")
            continue
    
    if model_path is None:
        print("[ERRO] Nenhum modelo disponível. Saindo...")
        return
    
    # Inicializa detector
    detector = CubeDetector(model_path)
    print("[INFO] Detector inicializado")
    
    # Inicializa logger
    logger = create_logger()
    detector.logger = logger
    print("[INFO] Logger criado")
    
    # Abre webcam
    cap = None
    for camera_id in [1, 0, 2, 3]:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            print(f"[INFO] Câmera aberta: ID {camera_id}")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            break
        else:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("[ERRO] Nenhuma câmera disponível. Saindo...")
        return

    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = time.time()
        
        # Detecta cubos
        detections = detector.detect_cubes(frame, current_time)
        
        # Desenha detecções para cubos ativos
        for color, cube_data in detector.active_cubes_by_color.items():
            x1, y1, x2, y2 = cube_data['bbox']
            
            # Cor do contorno baseada na cor detectada
            color_map = {
                'white': (255, 255, 255),
                'yellow': (0, 255, 255),
                'red': (0, 0, 255),
                'orange': (0, 165, 255),
                'blue': (255, 0, 0),
                'green': (0, 255, 0),
                'unknown': (128, 128, 128)
            }
            
            color_bgr = color_map.get(color, (128, 128, 128))
            face_name = detector.color_mapping.get(color, 'Desconhecida')
            
            # Desenha contorno
            cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, 3)
            
            # Calcula tempo na tela - usa último tempo visto se não foi detectado neste frame
            if cube_data['detected_this_frame']:
                time_in_frame = current_time - cube_data['entry_time']
            else:
                time_in_frame = cube_data['last_seen'] - cube_data['entry_time']
            
            # Texto com tempo e face (incluindo tempo de detecção)
            label = f"Cubo {color} | {time_in_frame:.1f}s | {face_name} (incl. detecção)"
            
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
        
        # Informações do grupo atual (minimalista)
        if hasattr(detector, 'logger'):
            group_info = detector.logger.get_current_group_info()
            if group_info['current_group_size'] > 0:
                # Mostra progresso do grupo atual
                progress_text = f"Grupo: {group_info['current_group_size']}/3"
                cv2.putText(frame, progress_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Mostra cores já detectadas
                if group_info['current_colors']:
                    colors_text = f"Cores: {', '.join(group_info['current_colors'])}"
                    cv2.putText(frame, colors_text, (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Mostra tempo total dos grupos finalizados
                if group_info['total_groups'] > 0:
                    total_groups_text = f"Grupos: {group_info['total_groups']}"
                    cv2.putText(frame, total_groups_text, (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Mostra informações de debug dos cubos sendo rastreados
                debug_y = 120
                for color, cube_data in detector.active_cubes_by_color.items():
                    if color in detector.cube_exit_frames:
                        exit_frames = detector.cube_exit_frames[color]
                        debug_text = f"{color}: {exit_frames}/{detector.min_exit_frames} frames sem detecção"
                        color_debug = (0, 255, 255) if exit_frames < detector.min_exit_frames else (0, 0, 255)
                        cv2.putText(frame, debug_text, (10, debug_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_debug, 1)
                        debug_y += 20
        
        # Mostra configurações de detecção atuais
        current_duration = detector.quick_detection_duration if detector.quick_detection_mode else detector.min_detection_duration
        current_frames = detector.quick_detection_frames if detector.quick_detection_mode else detector.min_consecutive_frames
        mode_text = "RÁPIDO" if detector.quick_detection_mode else "NORMAL"
        
        detection_time_text = f"Tempo: {current_duration:.1f}s"
        tolerance_text = f"Tolerância: {detector.max_missed_frames} frames"
        mode_display_text = f"Modo: {mode_text}"
        
        cv2.putText(frame, detection_time_text, (frame.shape[1] - 200, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, tolerance_text, (frame.shape[1] - 200, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, mode_display_text, (frame.shape[1] - 200, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if detector.quick_detection_mode else (255, 255, 255), 1)
        
        # Mostra progresso de detecção de cores em andamento
        if detector.color_detection_start:
            detection_y = frame.shape[0] - 100
            cv2.putText(frame, "DETECÇÃO EM ANDAMENTO:", (10, detection_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            detection_y += 25
            
            for color in detector.color_detection_start:
                current_time = time.time()
                detection_duration = current_time - detector.color_detection_start[color]
                progress = min(100, (detection_duration / detector.min_detection_duration) * 100)
                
                # Cor do texto baseada na cor do cubo
                color_map = {
                    'white': (255, 255, 255),
                    'yellow': (0, 255, 255),
                    'red': (0, 0, 255),
                    'orange': (0, 165, 255),
                    'blue': (255, 0, 0),
                    'green': (0, 255, 0)
                }
                text_color = color_map.get(color, (255, 255, 255))
                
                progress_text = f"{color.upper()}: {progress:.0f}% ({detection_duration:.1f}s)"
                cv2.putText(frame, progress_text, (10, detection_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
                detection_y += 20
        
        # Mostra controles de teclado
        controls_y = frame.shape[0] - 30
        controls_text = "Controles: Q=Sair, R=Modo Rápido, +/-=Tempo, [/]=Tolerância"
        cv2.putText(frame, controls_text, (10, controls_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Mostra frame
        cv2.imshow("Detecção de Cubos", frame)
        
        # Controles
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):  # Tecla 't' para testar ranges de cores
            if detections:
                detector.test_color_ranges(frame, detections[0]['bbox'])
        elif key == ord('d'):  # Tecla 'd' para toggle debug
            detector.debug_mode = not detector.debug_mode
        elif key == ord('f'):  # Tecla 'f' para finalizar grupo atual
            if hasattr(detector, 'logger'):
                detector.logger.force_finalize_group()
        elif key == ord('a'):  # Tecla 'a' para alternar envio para API
            if hasattr(detector, 'logger'):
                detector.logger.toggle_api_send()
        elif key == ord('+') or key == ord('='):  # Tecla '+' para aumentar tempo de detecção
            detector.min_detection_duration = min(2.0, detector.min_detection_duration + 0.1)
            detector.min_consecutive_frames = int(detector.min_detection_duration * 30)
            print(f"⏱️ Tempo de detecção aumentado para {detector.min_detection_duration:.1f}s")
        elif key == ord('-'):  # Tecla '-' para diminuir tempo de detecção
            detector.min_detection_duration = max(0.1, detector.min_detection_duration - 0.1)
            detector.min_consecutive_frames = int(detector.min_detection_duration * 30)
            print(f"⏱️ Tempo de detecção reduzido para {detector.min_detection_duration:.1f}s")
        elif key == ord('['):  # Tecla '[' para diminuir tolerância a frames perdidos
            detector.max_missed_frames = max(1, detector.max_missed_frames - 1)
            print(f"🎯 Tolerância a frames perdidos reduzida para {detector.max_missed_frames}")
        elif key == ord(']'):  # Tecla ']' para aumentar tolerância a frames perdidos
            detector.max_missed_frames = min(10, detector.max_missed_frames + 1)
            print(f"🎯 Tolerância a frames perdidos aumentada para {detector.max_missed_frames}")
        elif key == ord('r'):  # Tecla 'r' para alternar modo de detecção rápida
            detector.quick_detection_mode = not detector.quick_detection_mode
            mode_text = "ATIVADO" if detector.quick_detection_mode else "DESATIVADO"
            duration = detector.quick_detection_duration if detector.quick_detection_mode else detector.min_detection_duration
            frames = detector.quick_detection_frames if detector.quick_detection_mode else detector.min_consecutive_frames
            print(f"🚀 Modo de detecção rápida {mode_text} - {duration:.1f}s / {frames} frames")
    
    # Finaliza grupo restante se houver
    if hasattr(detector, 'logger') and detector.logger.current_group:
        detector.logger.force_finalize_group()
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()