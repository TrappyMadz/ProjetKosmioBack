"""
Configuration centralisée du logging pour l'application RAG.

Ce module fournit une configuration unifiée du logging avec :
- Sortie console avec coloration par niveau
- Sortie fichier avec rotation automatique (5 MB, 5 backups)
- Format standardisé : timestamp | niveau | service | message
"""

import logging
import os
from logging.handlers import RotatingFileHandler


# Configuration des couleurs pour la console (optionnel, désactivé sur Windows sans colorama)
class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Vert
        'WARNING': '\033[33m',   # Jaune
        'ERROR': '\033[31m',     # Rouge
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Ajouter la couleur selon le niveau
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname_colored = f"{color}{record.levelname:8}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "app.log",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5
):
    """
    Configure le logging pour toute l'application.
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Dossier pour les fichiers de logs
        log_file: Nom du fichier de log
        max_bytes: Taille maximale avant rotation (défaut: 5 MB)
        backup_count: Nombre de fichiers de backup à conserver
    """
    # Créer le dossier de logs s'il n'existe pas
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, log_file)
    
    # Format des logs
    file_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    console_format = "%(asctime)s | %(levelname_colored)s | %(name)-20s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Supprimer les handlers existants pour éviter les doublons
    root_logger.handlers = []
    
    # Handler Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    try:
        # Essayer d'utiliser le formatter coloré
        console_handler.setFormatter(ColoredFormatter(console_format, datefmt=date_format))
    except Exception:
        # Fallback sur un formatter simple si les couleurs ne fonctionnent pas
        console_handler.setFormatter(logging.Formatter(file_format, datefmt=date_format))
    root_logger.addHandler(console_handler)
    
    # Handler Fichier avec rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_format, datefmt=date_format))
    root_logger.addHandler(file_handler)
    
    # Réduire le niveau de log des bibliothèques tierces verbeuses
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    # Log initial
    root_logger.info(f"Logging configuré - Niveau: {log_level} - Fichier: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger avec le nom spécifié.
    
    Args:
        name: Nom du logger (généralement __name__ ou le nom du service)
        
    Returns:
        Logger configuré
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Message d'information")
    """
    return logging.getLogger(name)
