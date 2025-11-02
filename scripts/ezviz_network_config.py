#!/usr/bin/env python3
"""
Script de configuración automática para EZVIZ H6C Pro 2K
Configura IP estática, valida conectividad y prepara RTSP
"""

import subprocess
import socket
import requests
import time
import platform
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EzvizNetworkConfig:
    """Configurador de red para cámara EZVIZ"""
    
    def __init__(self):
        self.target_ip = "192.168.1.100"
        self.gateway = "192.168.1.1"
        self.rtsp_port = 554
        self.http_port = 80
        self.onvif_port = 80
        self.credentials = {
            'username': 'admin',
            'password': 'Abc123456'
        }
        
    def ping_host(self, host: str, timeout: int = 5) -> bool:
        """Verificar conectividad con ping"""
        try:
            if platform.system().lower() == "windows":
                cmd = f"ping -n 1 -w {timeout*1000} {host}"
            else:
                cmd = f"ping -c 1 -W {timeout} {host}"
                
            result = subprocess.run(
                cmd.split(), 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def scan_network_for_ezviz(self) -> Optional[str]:
        """Escanear red local buscando cámara EZVIZ"""
        print("🔍 Escaneando red local buscando cámara EZVIZ...")
        
        base_ip = "192.168.1."
        found_ips = []
        
        for i in range(100, 200):  # Escanear rango 192.168.1.100-199
            ip = f"{base_ip}{i}"
            
            if self.ping_host(ip, timeout=1):
                print(f"📡 Dispositivo encontrado en: {ip}")
                
                # Verificar si es cámara EZVIZ probando puerto RTSP
                if self.check_port_open(ip, self.rtsp_port):
                    print(f"✅ Cámara EZVIZ detectada en: {ip}")
                    found_ips.append(ip)
        
        if found_ips:
            return found_ips[0]  # Retornar primera cámara encontrada
        
        return None
    
    def check_port_open(self, host: str, port: int, timeout: int = 3) -> bool:
        """Verificar si puerto está abierto"""
        try:
            with socket.create_connection((host, port), timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def validate_camera_services(self, ip: str) -> Dict[str, bool]:
        """Validar servicios de la cámara"""
        services = {
            'rtsp': False,
            'http': False,
            'onvif': False
        }
        
        # Verificar RTSP (puerto 554)
        services['rtsp'] = self.check_port_open(ip, self.rtsp_port)
        
        # Verificar HTTP (puerto 80)
        services['http'] = self.check_port_open(ip, self.http_port)
        
        # Verificar ONVIF (puerto 80, mismo que HTTP)
        services['onvif'] = services['http']
        
        return services
    
    def test_rtsp_url(self, ip: str) -> Dict[str, Any]:
        """Probar URL RTSP con ffprobe"""
        rtsp_url = f"rtsp://{self.credentials['username']}:{self.credentials['password']}@{ip}:{self.rtsp_port}/h264/ch1/main/av_stream"
        
        result = {
            'url': rtsp_url,
            'accessible': False,
            'resolution': None,
            'fps': None,
            'codec': None
        }
        
        try:
            # Usar ffprobe para obtener información del stream
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-select_streams', 'v:0',
                '-probesize', '32', '-analyzeduration', '0',
                rtsp_url
            ]
            
            process = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            
            if process.returncode == 0:
                data = json.loads(process.stdout)
                if 'streams' in data and len(data['streams']) > 0:
                    stream = data['streams'][0]
                    
                    result['accessible'] = True
                    result['resolution'] = f"{stream.get('width', 'unknown')}x{stream.get('height', 'unknown')}"
                    result['fps'] = stream.get('r_frame_rate', 'unknown')
                    result['codec'] = stream.get('codec_name', 'unknown')
        
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout al probar RTSP")
        except json.JSONDecodeError:
            print("⚠️ Error al parsear respuesta de ffprobe")
        except FileNotFoundError:
            print("⚠️ ffprobe no encontrado - instalar ffmpeg")
            
        return result
    
    def generate_router_config_instructions(self) -> str:
        """Generar instrucciones para configurar IP estática en router"""
        return f"""
📶 CONFIGURACIÓN DE IP ESTÁTICA EN ROUTER

1. Acceder a la interfaz del router:
   http://{self.gateway}
   Usuario: admin (o revisar etiqueta del router)
   
2. Buscar sección:
   - "DHCP Reservation" o
   - "Static IP" o  
   - "IP Address Reservation"
   
3. Configurar:
   MAC Address: [Obtener de app EZVIZ o escaneo]
   IP Address: {self.target_ip}
   Description: EZVIZ H6C Pro 2K Camera
   
4. Aplicar cambios y reiniciar router si es necesario

5. Reiniciar cámara (desconectar/conectar alimentación)

6. Verificar con ping:
   ping {self.target_ip}
"""
    
    def run_configuration_wizard(self) -> Dict[str, Any]:
        """Ejecutar asistente de configuración completo"""
        print("🚀 Iniciando configuración EZVIZ H6C Pro 2K")
        print("=" * 60)
        
        config_result = {
            'timestamp': datetime.now().isoformat(),
            'target_ip': self.target_ip,
            'camera_found': False,
            'current_ip': None,
            'services_status': {},
            'rtsp_test': {},
            'recommendations': []
        }
        
        # 1. Verificar si cámara ya está en IP objetivo
        print(f"\n1️⃣ Verificando IP objetivo: {self.target_ip}")
        if self.ping_host(self.target_ip):
            print(f"✅ Cámara encontrada en IP objetivo: {self.target_ip}")
            config_result['camera_found'] = True
            config_result['current_ip'] = self.target_ip
        else:
            print(f"⚠️ No hay respuesta en IP objetivo: {self.target_ip}")
            
            # 2. Escanear red buscando cámara
            print("\n2️⃣ Escaneando red local...")
            found_ip = self.scan_network_for_ezviz()
            
            if found_ip:
                config_result['camera_found'] = True
                config_result['current_ip'] = found_ip
                config_result['recommendations'].append(
                    f"Configurar IP estática {self.target_ip} para {found_ip}"
                )
            else:
                print("❌ No se encontró cámara EZVIZ en la red")
                config_result['recommendations'].append(
                    "Verificar que la cámara esté conectada a Wi-Fi (LED azul fijo)"
                )
                return config_result
        
        # 3. Validar servicios
        current_ip = config_result['current_ip']
        print(f"\n3️⃣ Validando servicios en {current_ip}...")
        
        services = self.validate_camera_services(current_ip)
        config_result['services_status'] = services
        
        for service, status in services.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {service.upper()}: {'OK' if status else 'NO DISPONIBLE'}")
        
        # 4. Probar RTSP si está disponible
        if services['rtsp']:
            print(f"\n4️⃣ Probando stream RTSP...")
            rtsp_result = self.test_rtsp_url(current_ip)
            config_result['rtsp_test'] = rtsp_result
            
            if rtsp_result['accessible']:
                print(f"✅ RTSP funcionando:")
                print(f"   📐 Resolución: {rtsp_result['resolution']}")
                print(f"   🎬 FPS: {rtsp_result['fps']}")
                print(f"   🎥 Codec: {rtsp_result['codec']}")
            else:
                print("❌ RTSP no accesible")
                config_result['recommendations'].append(
                    "Habilitar RTSP en app EZVIZ y verificar credenciales"
                )
        
        # 5. Generar recomendaciones
        if not services.get('rtsp', False):
            config_result['recommendations'].append(
                "Habilitar RTSP en configuración avanzada de app EZVIZ"
            )
        
        if current_ip != self.target_ip:
            config_result['recommendations'].append(
                f"Configurar IP estática {self.target_ip} en router"
            )
        
        # 6. Mostrar resumen
        print(f"\n📋 RESUMEN DE CONFIGURACIÓN")
        print("=" * 60)
        print(f"Cámara encontrada: {'✅ Sí' if config_result['camera_found'] else '❌ No'}")
        print(f"IP actual: {config_result['current_ip'] or 'No detectada'}")
        print(f"IP objetivo: {config_result['target_ip']}")
        print(f"RTSP funcionando: {'✅ Sí' if config_result['rtsp_test'].get('accessible') else '❌ No'}")
        
        if config_result['recommendations']:
            print(f"\n⚠️ ACCIONES REQUERIDAS:")
            for i, rec in enumerate(config_result['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # 7. Mostrar instrucciones de configuración si es necesario
        if current_ip != self.target_ip:
            print(self.generate_router_config_instructions())
        
        return config_result
    
    def save_config_report(self, config_result: Dict[str, Any]) -> str:
        """Guardar reporte de configuración"""
        filename = f"ezviz_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado: {filename}")
        return filename

def main():
    """Función principal"""
    configurator = EzvizNetworkConfig()
    
    print("📹 EZVIZ H6C Pro 2K - Configuración Automática")
    print("=" * 60)
    print("Este script te ayudará a configurar tu cámara EZVIZ para obtener")
    print("un stream RTSP estable con resolución 2K @ 30fps")
    print("")
    
    # Ejecutar configuración
    result = configurator.run_configuration_wizard()
    
    # Guardar reporte
    report_file = configurator.save_config_report(result)
    
    # Mensaje final
    if result['camera_found'] and result['rtsp_test'].get('accessible'):
        print("\n🎉 ¡Configuración exitosa!")
        print("La cámara está lista para usar con el inference-service")
        rtsp_url = result['rtsp_test']['url']
        print(f"\n🔗 URL RTSP: {rtsp_url}")
    else:
        print("\n⚠️ Configuración incompleta")
        print("Revisar recomendaciones y ejecutar script nuevamente")
    
    return result

if __name__ == "__main__":
    main()