import os
import requests
from django.core.files.storage import Storage
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)


class ImgBBStorage(Storage):
    """Stockage personnalisé utilisant l'API ImgBB"""

    def __init__(self):
        self.api_key = getattr(settings, 'IMGBB_API_KEY', '')

    def _save(self, name, content):
        """Upload le fichier vers ImgBB et retourne l'URL publique"""
        try:
            # Lire le contenu en bytes
            data = content.read()
            response = requests.post(
                'https://api.imgbb.com/1/upload',
                params={'key': self.api_key},
                files={'image': (name, data)}
            )

            if response.status_code == 200:
                payload = response.json()
                if payload.get('success'):
                    img_url = payload['data']['url'] if 'url' in payload['data'] else payload['data'].get('image', {}).get('url')
                    logger.info(f"ImgBB upload success: {img_url}")
                    # Retourne l'URL publique comme identifiant
                    return img_url
                else:
                    logger.error(f"ImgBB API returned error: {payload}")
                    raise Exception(f"ImgBB error: {payload}")
            else:
                logger.error(f"ImgBB HTTP error: {response.status_code} - {response.text}")
                raise Exception(f"ImgBB HTTP error: {response.status_code}")

        except Exception as e:
            logger.exception(f"Failed to upload image to ImgBB: {e}")
            raise

    def url(self, name):
        """Retourne l'URL publique de l'image: ici `name` est déjà l'URL ImgBB"""
        return name

    def exists(self, name):
        """Considère que l'image existe si c'est déjà une URL"""
        return bool(name and name.startswith('http'))

    def delete(self, name):
        """Suppression non implémentée (ImgBB API nécessite gestion avancée)"""
        # Optionnel: implémenter suppression via ImgBB si nécessaire
        return None
