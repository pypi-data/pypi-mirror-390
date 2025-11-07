from bs4 import BeautifulSoup
from typing import Dict, Optional

import requests

from inatroget.config import Config

app_config = Config()


def get_carta_info_html(session: requests.Session, timeout: int = 10) -> str:
    """Retrieve the INATRO dashboard HTML containing driver license information."""
    response = session.get(app_config.ESTADO_CARTA_URL, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_carta_info(html_content: str) -> Dict[str, Optional[str]]:
    """
    Extract driving license information from INATRO HTML page.
    
    Args:
        html_content: HTML string content
        
    Returns:
        Dictionary with extracted information
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize result dictionary
    data = {
        'numero_carta': None,
        'nome_completo': None,
        'data_nascimento': None,
        'telefone': None,
        'endereco': None,
        'estado_carta': None,
        'data_inicio_validade': None,
        'data_fim_validade': None,
        'classes_carta': None,
        'categorias_carta': None
    }
    
    # Find all div elements with class col-md-4 mb-3
    info_divs = soup.find_all('div', class_='col-md-4 mb-3')
    
    for div in info_divs:
        h5 = div.find('h5')
        if not h5:
            continue
            
        label = h5.get_text(strip=True).lower()
        p = div.find('p')
        
        if not p:
            continue
        
        # Extract based on label
        if 'nº da carta de condução' in label or 'número da carta' in label:
            data['numero_carta'] = p.get_text(strip=True)
            
        elif 'nome completo' in label:
            data['nome_completo'] = p.get_text(strip=True)
            
        elif 'data de nascimento' in label:
            data['data_nascimento'] = p.get_text(strip=True)
            
        elif 'telefone' in label:
            data['telefone'] = p.get_text(strip=True)
            
        elif 'endereço' in label:
            data['endereco'] = p.get_text(strip=True)
            
        elif 'estado da carta' in label:
            # Extract from badge if exists
            badge = p.find('span', class_='badge')
            data['estado_carta'] = badge.get_text(strip=True) if badge else p.get_text(strip=True)
            
        elif 'data de ínicio de validade' in label or 'data de início de validade' in label:
            data['data_inicio_validade'] = p.get_text(strip=True) or None
            
        elif 'data de fim de validade' in label:
            data['data_fim_validade'] = p.get_text(strip=True) or None
            
        elif 'classes da carta' in label:
            data['classes_carta'] = p.get_text(strip=True)
            
        elif 'categorias da carta' in label:
            text = p.get_text(strip=True)
            data['categorias_carta'] = text if text and text != '-' else None
    
    return data
