import requests
import logging

class YandexDiskInfoService:
    API_URL = "https://cloud-api.yandex.net/v1/disk"

    @staticmethod
    def get_disk_info(token: str) -> str:
        headers = {
            "Authorization": f"OAuth {token}",
            "Accept": "application/json"
        }
        try:
            response = requests.get(
                YandexDiskInfoService.API_URL, 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            gb = 1024 ** 3
            
            total = round(data['total_space'] / gb, 2)
            used = round(data['used_space'] / gb, 2)
            trash = round(data['trash_size'] / gb, 2)
            free = round((data['total_space'] - data['used_space']) / gb, 2)

            return (f"<ul>"
                    f"  <li>Всего: {total} ГБ\n</li>"
                    f"  <li>Занято: {used} ГБ\n</li>"
                    f"  <li>Свободно: {free} ГБ\n</li>"
                    f"  <li>В корзине: {trash} ГБ</li>"
                    f"</ul>")
                    
        except Exception as e:
            logging.error(f"Yandex Disk API Error: {e}")
            return "Не удалось получить информацию о Диске. Попробуйте позже."