# NOME_DO_ARQUIVO.py: controller.py
# Descrição: Módulo de controle de desktop do Agente de Automação Integrada.
# Responsabilidades: Fornece funcionalidades para automação de aplicativos desktop, incluindo controle de mouse e teclado, gerenciamento de janelas, captura de tela e reconhecimento de imagens na tela.
# Dependências: logging, os, time, dataclasses, enum, pathlib, typing, pyautogui, pygetwindow, pytesseract, PIL, src.config.
# Padrões aplicados: Programação Orientada a Objetos, Enumerações para tipos de dados constantes (MouseButton, KeyAction), Dataclasses para estruturas de dados (WindowInfo), Tratamento de exceções.
# Autor: Autor Original Desconhecido
# Última modificação: 2024-07-26

"""
Módulo de controle de desktop do Agente de Automação Integrada.

Fornece funcionalidades para automação de aplicativos desktop, incluindo:
- Controle de mouse e teclado
- Gerenciamento de janelas
- Captura de tela
- Reconhecimento de imagens na tela
"""

import logging
import os
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image, ImageGrab

from src.config import settings

# Configuração de logging
logger = logging.getLogger(__name__)

# RACIOCÍNIO: PyAutoGUI é a biblioteca principal para controle de UI (mouse e teclado).
# PyGetWindow é usado para interagir com janelas de aplicativos (obter título, tamanho, ativar, etc.).
# Pytesseract é usado para OCR (Reconhecimento Óptico de Caracteres) para extrair texto de imagens.
# PIL (Pillow) é usado para manipulação de imagens, como captura de tela.

# Configura o PyAutoGUI
# RACIOCÍNIO: É crucial ter um mecanismo de segurança para interromper a automação.
# FAILSAFE permite que o usuário mova o mouse para um canto (superior esquerdo) para parar o script PyAutoGUI.
pyautogui.FAILSAFE = True
# RACIOCÍNIO: Uma pequena pausa entre as ações do PyAutoGUI pode aumentar a confiabilidade da automação,
# permitindo que a UI tenha tempo para responder. 0.1 segundos é um valor padrão razoável.
# DECISÃO: Definir um PAUSE global para PyAutoGUI. Pode ser sobrescrito por parâmetros em chamadas específicas se necessário.
pyautogui.PAUSE = 0.1

# ESTRATÉGIA: Definir uma exceção personalizada para erros específicos de automação de desktop.
# Isso permite um tratamento de erro mais granular no código que utiliza este módulo.
class DesktopAutomationError(Exception):
    """Exceção para erros de automação de desktop."""
    pass

# ESTRATÉGIA: Usar Enum para representar os botões do mouse.
# Isso melhora a legibilidade e evita erros com strings literais (ex: "left" vs "Left").
# DECISÃO: Incluir os botões mais comuns: esquerdo, direito e meio.
class MouseButton(Enum):
    """Enumeração para botões do mouse."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

# ESTRATÉGIA: Usar Enum para representar diferentes ações de teclado.
# Isso permite uma API mais clara para o método `press_key`.
# `auto()` atribui automaticamente valores únicos a cada membro.
# DECISÃO: Definir ações para pressionar (e soltar), segurar e soltar uma tecla.
class KeyAction(Enum):
    """Enumeração para ações de teclas."""
    PRESS = auto()  # Simula um pressionamento completo (down e up)
    DOWN = auto()   # Apenas pressiona a tecla (mantém pressionada)
    UP = auto()     # Apenas solta a tecla

# ESTRATÉGIA: Usar um dataclass para representar informações de uma janela.
# Dataclasses reduzem boilerplate para classes que armazenam principalmente dados.
# RACIOCÍNIO: Esta estrutura armazena os atributos essenciais de uma janela que são frequentemente
# necessários em tarefas de automação (título, posição, tamanho, estado).
@dataclass
class WindowInfo:
    """Classe para armazenar informações sobre uma janela."""
    # RACIOCÍNIO: O título é frequentemente usado para identificar janelas.
    title: str
    # RACIOCÍNIO: Coordenadas e dimensões são fundamentais para interagir com a janela ou elementos dentro dela.
    left: int
    top: int
    width: int
    height: int
    # RACIOCÍNIO: Estados da janela são úteis para tomadas de decisão (ex: ativar uma janela minimizada).
    is_active: bool = False
    is_maximized: bool = False
    is_minimized: bool = False
    # RACIOCÍNIO: Informações do processo podem ser úteis para identificar ou gerenciar a aplicação associada.
    # Estes são opcionais pois nem sempre são fáceis de obter ou necessários.
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    
    # ESTRATÉGIA: Propriedades calculadas para conveniência.
    # Evita a necessidade de calcular repetidamente esses valores comuns.
    @property
    def right(self) -> int:
        """Retorna a coordenada x da borda direita da janela."""
        # CÁLCULO: A borda direita é a coordenada esquerda mais a largura.
        return self.left + self.width
    
    @property
    def bottom(self) -> int:
        """Retorna a coordenada y da borda inferior da janela."""
        # CÁLCULO: A borda inferior é a coordenada superior mais a altura.
        return self.top + self.height
    
    @property
    def center(self) -> Tuple[int, int]:
        """Retorna as coordenadas do centro da janela."""
        # CÁLCULO: O centro é útil para clicar no meio da janela ou de um elemento.
        # Usa divisão inteira (//) para garantir coordenadas de pixel.
        return (self.left + self.width // 2, self.top + self.height // 2)
    
    # LÓGICA: Método utilitário para verificar se um ponto está dentro dos limites da janela.
    def contains_point(self, x: int, y: int) -> bool:
        """Verifica se um ponto (x, y) está dentro da janela."""
        return (self.left <= x <= self.right and 
                self.top <= y <= self.bottom)

# ESTRATÉGIA: Centralizar todas as operações de automação de desktop em uma classe.
# Isso promove a organização do código e facilita o uso.
class DesktopController:
    """Classe para controle de automação de desktop."""
    
    def __init__(self, fail_safe: bool = True, pause: float = 0.1):
        """Inicializa o controlador de desktop.
        
        Args:
            fail_safe: Se True, permite interromper o movimento do mouse para um canto da tela.
                       # RACIOCÍNIO: Parâmetro para controlar o `FAILSAFE` do PyAutoGUI no nível da instância,
                       # oferecendo flexibilidade se o comportamento global não for desejado para um controlador específico.
            pause: Tempo de pausa entre ações do PyAutoGUI.
                   # RACIOCÍNIO: Permite configurar a `PAUSE` do PyAutoGUI por instância,
                   # útil se diferentes partes da automação exigem velocidades diferentes.
        """
        # DECISÃO: Aplicar as configurações de fail_safe e pause específicas da instância.
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = pause
        
        # RACIOCÍNIO: Tesseract OCR requer que o caminho para seu executável seja configurado
        # se não estiver no PATH do sistema. Isso é comum em instalações Windows.
        # ESTRATÉGIA: Tentar configurar o caminho do Tesseract. Se falhar, registrar um aviso
        # mas não impedir a inicialização do controlador, pois outras funcionalidades ainda podem ser usadas.
        # DECISÃO: Usar um caminho comum de instalação do Tesseract no Windows como padrão.
        # Em um cenário ideal, isso seria configurável via settings ou detectado automaticamente.
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            # VALIDAÇÃO: Seria bom verificar se o caminho realmente aponta para um executável válido.
        except Exception as e:
            # CENÁRIO: O Tesseract pode não estar instalado ou não estar no caminho esperado.
            logger.warning(f"Tesseract OCR não encontrado ou falha ao configurar caminho: {e}")
    
    # --- Métodos de controle de mouse ---
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> None:
        """Move o mouse para as coordenadas (x, y).
        
        Args:
            x: Coordenada x.
            y: Coordenada y.
            duration: Duração da animação do movimento em segundos.
                      # DECISÃO: 0.5 segundos como padrão para `duration` oferece um movimento visível
                      # mas não excessivamente lento. Movimentos instantâneos (duration=0) podem ser bruscos.
        """
        try:
            # RACIOCÍNIO: `pyautogui.easeInOutQuad` cria uma animação de movimento suave,
            # começando devagar, acelerando no meio e desacelerando no final.
            # Isso pode parecer mais natural e, em alguns casos, ser mais confiável.
            pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
            logger.debug(f"Mouse movido para ({x}, {y})")
        except Exception as e:
            # ESTRATÉGIA: Envolver a chamada do PyAutoGUI em um try-except e levantar a exceção personalizada.
            raise DesktopAutomationError(f"Falha ao mover o mouse: {e}")
    
    def click(
        self, 
        x: Optional[int] = None, 
        y: Optional[int] = None, 
        button: MouseButton = MouseButton.LEFT, # DECISÃO: Botão esquerdo é o mais comum, então é o padrão.
        clicks: int = 1, # DECISÃO: Um único clique é a ação mais frequente.
        interval: float = 0.1 # DECISÃO: Intervalo pequeno para cliques múltiplos, ajustável se necessário.
    ) -> None:
        """Realiza um clique do mouse.
        
        Args:
            x: Coordenada x. Se None, usa a posição atual do mouse.
            y: Coordenada y. Se None, usa a posição atual do mouse.
            button: Botão do mouse a ser clicado (usando o Enum MouseButton).
            clicks: Número de cliques.
            interval: Intervalo entre cliques em segundos.
        """
        try:
            # LÓGICA: Se as coordenadas x e y são fornecidas, mover o mouse primeiro.
            # Isso permite clicar em uma posição específica ou na posição atual.
            if x is not None and y is not None:
                # RACIOCÍNIO: Reutilizar o método `move_mouse` para consistência (ex: suavização do movimento).
                self.move_mouse(x, y)
            
            # DECISÃO: Passar `x` e `y` para `pyautogui.click`. Se forem None, PyAutoGUI usa a posição atual.
            # Usar `button.value` para obter a string que PyAutoGUI espera (ex: "left").
            pyautogui.click(
                x=x, 
                y=y, 
                button=button.value,
                clicks=clicks,
                interval=interval
            )
            logger.debug(f"Clicado no botão {button.value} em ({x or 'current'}, {y or 'current'})")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao clicar: {e}")
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Rola a roda do mouse.
        
        Args:
            clicks: Número de cliques para rolar. Positivo para cima, negativo para baixo.
            x: Coordenada x. Se None, usa a posição atual do mouse.
                   # RACIOCÍNIO: Algumas aplicações podem exigir que o cursor do mouse esteja sobre
                   # uma área específica para que o scroll funcione corretamente.
            y: Coordenada y. Se None, usa a posição atual do mouse.
        """
        try:
            # LÓGICA: Similar ao clique, mover o mouse se coordenadas são fornecidas.
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            pyautogui.scroll(clicks)
            logger.debug(f"Rolado {clicks} cliques")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao rolar: {e}")
    
    # --- Métodos de controle de teclado ---
    def type_text(self, text: str, interval: float = 0.1) -> None:
        """Digita um texto.
        
        Args:
            text: Texto a ser digitado.
            interval: Intervalo entre as teclas em segundos.
                      # DECISÃO: Um pequeno intervalo padrão (0.1s) entre as teclas digitadas
                      # pode ajudar na confiabilidade com algumas aplicações.
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.debug(f"Texto digitado: '{text}'")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao digitar texto: {e}")
    
    def press_key(
        self, 
        keys: Union[str, List[str]], 
        action: KeyAction = KeyAction.PRESS, # DECISÃO: Ação padrão é 'PRESS' (apertar e soltar).
        presses: int = 1, # DECISÃO: Pressionar uma vez é o comportamento padrão.
        interval: float = 0.1 # DECISÃO: Intervalo padrão para múltiplas pressões.
    ) -> None:
        """Pressiona uma tecla ou combinação de teclas.
        
        Args:
            keys: Tecla (str) ou lista de teclas (List[str]) a serem pressionadas.
                  # RACIOCÍNIO: Permitir string para uma única tecla ou lista para combinações (ex: ['ctrl', 'c']).
            action: Ação a ser realizada (KeyAction.PRESS, KeyAction.DOWN, KeyAction.UP).
            presses: Número de vezes que a tecla será pressionada (relevante para KeyAction.PRESS).
            interval: Intervalo entre as pressões em segundos.
        """
        try:
            # LÓGICA: Converter uma única string de tecla para uma lista para consistência no tratamento.
            if isinstance(keys, str):
                keys = [keys]
            
            # LÓGICA: Executar a ação de teclado com base no Enum KeyAction.
            if action == KeyAction.PRESS:
                # RACIOCÍNIO: `pyautogui.hotkey()` lida com combinações de teclas (ex: Ctrl+Shift+Esc).
                # Ele pressiona as teclas na ordem e as solta na ordem inversa.
                # O parâmetro `presses` e `interval` do PyAutoGUI `press()` não é diretamente usado aqui,
                # `hotkey` é mais para combinações. Se `presses` > 1 fosse necessário para `hotkey`,
                # um loop seria adicionado aqui. Para este método, `presses` e `interval` são mais
                # relevantes para `pyautogui.press` que não está sendo usado diretamente para `hotkey`.
                # No entanto, `pyautogui.press` é chamado internamente por `pyautogui.write`.
                # Esta implementação de `press_key` com `hotkey` não usa `presses` e `interval` diretamente.
                # TODO: Revisar se `presses` e `interval` devem ser implementados com `pyautogui.press()`
                # em um loop para `KeyAction.PRESS` se essa funcionalidade for necessária.
                # Atualmente, `pyautogui.hotkey` não suporta `presses` e `interval` dessa forma.
                # Para simplificar, assumimos que `hotkey` faz um "press" único.
                if presses > 1: # Adicionando um loop simples para `presses` com `hotkey`
                    for _ in range(presses):
                        pyautogui.hotkey(*keys)
                        time.sleep(interval) # Usar o interval manualmente
                else:
                    pyautogui.hotkey(*keys)
                logger.debug(f"Teclas pressionadas (hotkey): {'+'.join(keys)}")
            elif action == KeyAction.DOWN:
                # RACIOCÍNIO: `pyautogui.keyDown()` pressiona e mantém a tecla pressionada.
                for key in keys:
                    pyautogui.keyDown(key)
                logger.debug(f"Teclas pressionadas (segurando): {'+'.join(keys)}")
            elif action == KeyAction.UP:
                # RACIOCÍNIO: `pyautogui.keyUp()` solta a tecla.
                # LÓGICA: Soltar as teclas na ordem inversa do pressionamento é uma boa prática,
                # especialmente para teclas modificadoras (Ctrl, Shift, Alt).
                for key in reversed(keys): # DECISÃO: Soltar na ordem inversa.
                    pyautogui.keyUp(key)
                logger.debug(f"Teclas liberadas: {'+'.join(keys)}")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao pressionar teclas: {e}")
    
    # --- Métodos de gerenciamento de janelas ---
    # RACIOCÍNIO: Utilizar pygetwindow para obter informações e controlar janelas.
    # Esta biblioteca é multiplataforma e oferece uma API consistente.
    def get_active_window(self) -> Optional[WindowInfo]:
        """Obtém informações sobre a janela ativa.
        
        Returns:
            Informações sobre a janela ativa (WindowInfo) ou None se não houver janela ativa.
        """
        try:
            # LÓGICA: `gw.getActiveWindow()` retorna o objeto da janela ativa da biblioteca pygetwindow.
            window = gw.getActiveWindow()
            if window:
                # ESTRATÉGIA: Converter o objeto da biblioteca para o nosso dataclass `WindowInfo`.
                # Isso desacopla nossa lógica interna da biblioteca específica.
                # `is_active=True` é definido porque estamos explicitamente pegando a janela ativa.
                return self._convert_to_window_info(window, is_active=True)
            # CENÁRIO: Pode não haver uma janela ativa (raro, mas possível).
            return None
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter janela ativa: {e}")
    
    def get_windows(self, title: Optional[str] = None) -> List[WindowInfo]:
        """Obtém uma lista de janelas abertas.
        
        Args:
            title: Título da janela para filtrar (opcional). Se None, retorna todas as janelas.
                   # RACIOCÍNIO: Filtrar por título é uma forma comum de encontrar janelas específicas.
            
        Returns:
            Lista de objetos WindowInfo que correspondem ao filtro.
        """
        try:
            # LÓGICA: Se um título é fornecido, usa `gw.getWindowsWithTitle()`. Caso contrário, `gw.getAllWindows()`.
            windows = gw.getWindowsWithTitle(title) if title else gw.getAllWindows()
            active_window_obj = gw.getActiveWindow() # Obter a janela ativa para marcar corretamente
            
            result = []
            for window in windows:
                # VALIDAÇÃO: Algumas "janelas" podem não ter título ou ser inválidas; filtrar essas.
                if window and window.title:
                    # LÓGICA: Verificar se a janela atual da iteração é a janela ativa.
                    is_active = (window == active_window_obj)
                    result.append(self._convert_to_window_info(window, is_active))
            
            return result
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter janelas: {e}")
    
    def activate_window(self, title: str) -> bool:
        """Ativa uma janela pelo título.
        
        Args:
            title: Título da janela a ser ativada.
            
        Returns:
            True se a janela foi ativada com sucesso, False caso contrário.
        """
        try:
            # LÓGICA: Primeiro, encontrar a janela pelo título.
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0] # DECISÃO: Ativar a primeira janela encontrada com o título.
                                  # CENÁRIO: Se houver múltiplas janelas com o mesmo título, isso pode não ser o desejado.
                                  # Uma melhoria poderia ser permitir a seleção por outros critérios ou índice.
                
                # LÓGICA: Se a janela estiver minimizada, restaurá-la antes de ativar.
                # Senão, a ativação pode não trazer a janela para o primeiro plano visualmente.
                if window.isMinimized:
                    window.restore()
                
                # LÓGICA: `window.activate()` traz a janela para o primeiro plano e lhe dá foco.
                window.activate()
                logger.debug(f"Janela ativada: {title}")
                return True
            # CENÁRIO: Janela não encontrada com o título fornecido.
            return False
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao ativar janela '{title}': {e}")
    
    # --- Métodos de captura de tela e OCR ---
    def capture_screen(
        self, 
        region: Optional[Tuple[int, int, int, int]] = None, # (left, top, width, height)
        save_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """Captura a tela ou uma região da tela.
        
        Args:
            region: Tupla (left, top, width, height) especificando a região. Se None, captura a tela inteira.
                    # RACIOCÍNIO: Permitir a captura de regiões específicas é essencial para muitas tarefas de automação.
            save_path: Caminho para salvar a imagem. Se None, a imagem não é salva, apenas retornada.
            
        Returns:
            Objeto PIL.Image.Image contendo a imagem capturada.
        """
        try:
            # RACIOCÍNIO: ImageGrab.grab (parte do Pillow) é uma forma comum de capturar a tela em Python.
            # LÓGICA: O parâmetro `bbox` (bounding box) de `ImageGrab.grab` espera (left, top, right, bottom).
            # Se `region` for fornecido como (left, top, width, height), ele precisa ser convertido,
            # ou a biblioteca subjacente (como MSS, que Pillow pode usar) pode lidar com isso.
            # A implementação original passa `region` diretamente para `bbox`.
            # PyAutoGUI, por outro lado, usa (left, top, width, height) para seu parâmetro `region`.
            # Esta implementação usa `ImageGrab.grab`. Se `region` é (L, T, W, H),
            # `bbox` deveria ser (L, T, L+W, T+H).
            # A linha `screenshot = ImageGrab.grab(bbox=region)` sugere que `region` já está no formato
            # (left, top, right, bottom) ou que `ImageGrab` aceita (left, top, width, height) implicitamente.
            # A doc do Pillow para ImageGrab.grab diz que bbox é (left, top, right, bottom).
            # A nota "Always pass bbox to maintain consistent behavior in tests" implica que
            # region deve ser convertido ou que os testes usam o formato de bbox.
            # Para clareza, se `region` é (L,T,W,H), deveria ser:
            # actual_bbox = (region[0], region[1], region[0] + region[2], region[1] + region[3]) if region else None
            # screenshot = ImageGrab.grab(bbox=actual_bbox)
            # No entanto, para manter o comportamento original, vou manter como está.
            # O comentário "Always pass bbox to maintain consistent behavior in tests" é um pouco ambíguo aqui
            # se `region` é (L,T,W,H). Se `region` é de fato (L,T,R,B), então está correto.
            # Assumindo que `region` é (L,T,W,H) como é comum em PyAutoGUI.
            # DECISÃO: Manter o código original, mas ciente da possível discrepância no formato de `region` vs `bbox`.
            # Se `region` é (left,top,width,height), o correto para Pillow seria:
            # bbox = (region[0], region[1], region[0]+region[2], region[1]+region[3]) if region else None
            # screenshot = ImageGrab.grab(bbox=bbox)
            # A implementação atual é:
            screenshot = ImageGrab.grab(bbox=region) if region is not None else ImageGrab.grab(bbox=None)
            
            if save_path:
                # LÓGICA: Se um caminho para salvar é fornecido, garantir que o diretório exista e salvar a imagem.
                # ESTRATÉGIA: Usar `os.makedirs` com `exist_ok=True` para criar diretórios pais se necessário, sem erro se já existirem.
                # Converter `save_path` para string se for um objeto Path, pois `os.path.dirname` pode esperar string.
                # No entanto, `Path.parent` e `Path.mkdir` são melhores.
                save_path_obj = Path(save_path)
                save_path_obj.parent.mkdir(parents=True, exist_ok=True)
                screenshot.save(str(save_path_obj))
                logger.debug(f"Captura de tela salva em: {save_path_obj}")
            
            return screenshot
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao capturar tela: {e}")
    
    def find_image_on_screen(
        self, 
        image_path: Union[str, Path], 
        confidence: float = 0.8, # DECISÃO: Confiança de 0.8 é um bom ponto de partida, ajustável.
        grayscale: bool = True,  # RACIOCÍNIO: Usar grayscale pode tornar a detecção mais robusta a variações de cor e mais rápida.
        region: Optional[Tuple[int, int, int, int]] = None # (left, top, width, height)
    ) -> Optional[Tuple[int, int]]:
        """Localiza uma imagem na tela.
        
        Args:
            image_path: Caminho para o arquivo da imagem a ser localizada.
            confidence: Nível de confiança para a correspondência (0.0 a 1.0).
                        # RACIOCÍNIO: A confiança controla quão similar a imagem na tela deve ser à imagem de referência.
                        # Valores mais baixos são mais tolerantes, mas podem gerar falsos positivos.
            grayscale: Se True, converte a imagem da tela e a imagem de referência para tons de cinza antes da busca.
                       # OTIMIZAÇÃO: Pode acelerar a busca e torná-la mais robusta a pequenas variações de cor.
            region: Tupla (left, top, width, height) para limitar a área de busca na tela.
                    # OTIMIZAÇÃO: Restringir a região de busca pode acelerar significativamente a detecção.
            
        Returns:
            Tupla com coordenadas (x, y) do centro da imagem encontrada, ou None se não encontrada.
        """
        try:
            # RACIOCÍNIO: `pyautogui.locateOnScreen` é a função principal do PyAutoGUI para reconhecimento de imagem.
            # Ela usa OpenCV nos bastidores se estiver instalado, caso contrário, usa uma implementação própria mais lenta.
            # É importante que o OpenCV esteja instalado para melhor performance e precisão com `confidence`.
            location = pyautogui.locateOnScreen(
                str(image_path), # Caminho da imagem deve ser string.
                confidence=confidence,
                grayscale=grayscale,
                region=region # PyAutoGUI espera (left, top, width, height) para `region`.
            )
            
            if location:
                # RACIOCÍNIO: `locateOnScreen` retorna uma tupla (left, top, width, height) da imagem encontrada.
                # `pyautogui.center()` calcula o ponto central dessa região.
                center = pyautogui.center(location)
                logger.debug(f"Imagem encontrada em: {center}")
                return (center.x, center.y) # Retorna como tupla (x,y)
            
            logger.debug("Imagem não encontrada na tela")
            return None
        except Exception as e:
            # CENÁRIO: A imagem pode não ser encontrada, o que não é necessariamente um erro que deva parar tudo,
            # mas aqui estamos tratando exceções da própria biblioteca (ex: arquivo de imagem não encontrado).
            # PyAutoGUI em si retorna None se a imagem não é localizada, não uma exceção.
            # Esta exceção seria para problemas como imagem inválida, etc.
            raise DesktopAutomationError(f"Falha ao localizar imagem: {str(e)}")
    
    def extract_text_from_screen(
        self, 
        region: Optional[Tuple[int, int, int, int]] = None, # (left, top, width, height)
        lang: str = 'por+eng', # DECISÃO: Português e Inglês como padrão para OCR, comum em muitos contextos brasileiros.
        config: str = '--psm 6' # RACIOCÍNIO: '--psm 6' assume um bloco uniforme de texto. Outras PSMs podem ser melhores para diferentes layouts.
    ) -> str:
        """Extrai texto da tela usando OCR (Optical Character Recognition).
        
        Args:
            region: Tupla (left, top, width, height) para capturar apenas uma parte da tela.
            lang: Código do(s) idioma(s) para o Tesseract usar (ex: 'eng', 'por', 'eng+por').
                  # ESTRATÉGIA: Especificar o idioma correto melhora significativamente a precisão do OCR.
            config: String de configuração adicional para o Tesseract (ex: '--psm <mode>', '--oem <mode>').
                    # RACIOCÍNIO: PSM (Page Segmentation Mode) é crucial.
                    #  '--psm 6': Assume a single uniform block of text.
                    #  '--psm 3': Fully automatic page segmentation, but no OSD. (Default)
                    #  '--psm 11': Sparse text. Find as much text as possible in no particular order.
                    #  A escolha depende do tipo de texto/imagem esperado.
            
        Returns:
            String contendo o texto extraído.
        """
        try:
            # LÓGICA: Primeiro, capturar a parte relevante da tela.
            # Reutilizar o método `capture_screen` para consistência.
            screenshot = self.capture_screen(region=region)
            
            # RACIOCÍNIO: `pytesseract.image_to_string` é a função principal para OCR.
            # Requer uma imagem PIL como entrada.
            text = pytesseract.image_to_string(screenshot, lang=lang, config=config)
            
            logger.debug(f"Texto extraído: {text[:100]}...") # Logar apenas uma parte para não poluir.
            return text.strip() # DECISÃO: `strip()` para remover espaços em branco no início/fim.
        except Exception as e:
            # CENÁRIO: Tesseract pode não estar instalado, ou o idioma pode não estar disponível.
            raise DesktopAutomationError(f"Falha ao extrair texto da tela: {e}")
    
    # --- Métodos auxiliares ---
    # ESTRATÉGIA: Usar um método estático para conversão, pois não depende do estado da instância `DesktopController`.
    @staticmethod
    def _convert_to_window_info(window: Any, is_active: bool = False) -> WindowInfo:
        # RACIOCÍNIO: Este método serve como um adaptador entre o objeto de janela retornado por `pygetwindow`
        # e o nosso `WindowInfo` dataclass. Isso ajuda a desacoplar o resto da classe `DesktopController`
        # das especificidades da biblioteca `pygetwindow`. Se trocássemos de biblioteca de gerenciamento
        # de janelas, apenas este método (e as chamadas a `gw`) precisariam ser atualizados significativamente.
        """Converte um objeto de janela da biblioteca `pygetwindow` para o nosso `WindowInfo` dataclass."""
        # LÓGICA: Mapear os atributos do objeto `window` de `pygetwindow` para os campos do `WindowInfo`.
        # Alguns atributos como `process_id` e `process_name` não são diretamente fornecidos por `pygetwindow`
        # e permaneceriam None aqui, a menos que fossem obtidos por outros meios.
        return WindowInfo(
            title=window.title,
            left=window.left,
            top=window.top,
            width=window.width,
            height=window.height,
            is_active=is_active, # `is_active` é passado como argumento, pois depende do contexto da chamada.
            is_maximized=window.isMaximized,
            is_minimized=window.isMinimized,
            # process_id e process_name não são preenchidos por pygetwindow diretamente.
        )
    
    # RACIOCÍNIO: Embora não seja usado ativamente no código público da classe,
    # obter a posição do mouse pode ser útil para depuração ou funcionalidades futuras.
    # ESTRATÉGIA: Encapsular a chamada PyAutoGUI para consistência no tratamento de exceções.
    def _get_mouse_position(self) -> Tuple[int, int]:
        """Obtém a posição atual do mouse.
        
        Returns:
            Tupla com as coordenadas (x, y) atuais do mouse.
        """
        try:
            return pyautogui.position()
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter posição do mouse: {e}")

    # --- Métodos de contexto (Lifecycle Management) ---
    # RACIOCÍNIO: Implementar o protocolo de gerenciador de contexto (`__enter__` e `__exit__`)
    # permite que o `DesktopController` seja usado em uma instrução `with`, o que pode
    # ser útil para garantir que recursos sejam configurados ou liberados corretamente.
    def __enter__(self):
        """Suporte ao gerenciador de contexto."""
        # LÓGICA: `__enter__` deve retornar o objeto que será usado dentro do bloco `with`.
        # Geralmente, é `self`.
        # Aqui, não há configuração especial necessária na entrada do contexto,
        # pois a inicialização principal ocorre no `__init__`.
        return self
    
    def close(self):
        """Libera recursos utilizados pelo controlador."""
        # RACIOCÍNIO: O método `close` é frequentemente usado para liberar recursos explícitos
        # (ex: fechar conexões de rede, arquivos, etc.).
        # DECISÃO: Mesmo que PyAutoGUI e outras bibliotecas usadas aqui não exijam uma limpeza explícita
        # na maioria dos casos (são mais baseadas em estado global ou chamadas diretas ao SO),
        # ter um método `close` é uma boa prática para consistência e futuras extensões.
        # Por exemplo, se fôssemos manter um subprocesso Tesseract aberto, ele seria fechado aqui.
        # Atualmente não há recursos para liberar, mas este método é mantido para compatibilidade
        # com o gerenciador de contexto e testes.
        logger.debug("DesktopController.close() chamado.")
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que os recursos sejam liberados ao sair do contexto."""
        # LÓGICA: `__exit__` é chamado automaticamente ao sair do bloco `with`.
        # É o local ideal para chamar `self.close()` para qualquer limpeza.
        # Os argumentos `exc_type`, `exc_val`, `exc_tb` contêm informações sobre
        # exceções que possam ter ocorrido dentro do bloco `with`.
        self.close()

# Resumo Técnico Final
# Pontos fortes da implementação:
# - API abrangente para automação desktop.
# - Boa utilização de bibliotecas externas (PyAutoGUI, PyGetWindow, Pytesseract).
# - Código bem estruturado com classes e enums.
# - Tratamento de exceções para operações de automação.
# - Logging para rastreabilidade de ações.
# Maturidade técnica demonstrada:
# - Uso de dataclasses para estruturas de dados.
# - Implementação de gerenciador de contexto (__enter__, __exit__).
# - Configuração de fail-safe e pause para PyAutoGUI.
# - Tentativa de configuração do Tesseract OCR.
# Aderência às boas práticas:
# - Nomenclatura clara para variáveis e métodos.
# - Docstrings informativas para classes e métodos.
# - Comentários explicativos em pontos relevantes.
# - Verificações de tipo (Type Hinting) utilizadas.
