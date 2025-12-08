import requests
import logging

class YandexDisсResourcesService:
    API_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    @staticmethod
    def get_file_list(token: str, path: str = "/") -> str:
        headers = {
            "Authorization": f"OAuth {token}",
            "Accept": "application/json"
        }
        params = {
            "path": path,
            "limit": 100,
            "sort": "type"
        }
        
        try:
            response = requests.get(
                YandexDisсResourcesService.API_URL, 
                headers=headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('_embedded', {}).get('items', [])
            
            if not items:
                return "Папка пуста."

            result = "<ul>"
            for item in items:
                name = item.get('name')
                is_dir = item.get('type') == 'dir'
                
                if is_dir:
                    type_label = "Папка"
                    size_info = ""
                else:
                    type_label = "Файл"
                    size_bytes = item.get('size', 0)
                    size_info = f" — {YandexDisсResourcesService._format_size(size_bytes)}"

                result += f"\n  <li>{type_label}: {name}{size_info}</li>"
            
            result += "\n</ul>"
            return result
                    
        except Exception as e:
            logging.error(f"Yandex Disk API Error: {e}")
            return "Не удалось получить список файлов. Попробуйте позже."

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 Б"
        
        units = ("Б", "КБ", "МБ", "ГБ", "ТБ")
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
            
        return f"{round(size, 2)} {units[i]}"