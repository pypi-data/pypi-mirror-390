#!/usr/bin/env python3
"""
Полный тест всех режимов MCP Proxy Adapter
"""
import requests
import subprocess
import time
import json
from typing import Dict, Any, List, Tuple

class MCPProxyTester:
    """Тестер всех режимов MCP Proxy Adapter"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.results: List[Dict[str, Any]] = []
        
    def cleanup(self):
        """Очистка процессов"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        self.processes.clear()
        
    def test_http_basic(self) -> Dict[str, Any]:
        """Тест HTTP Basic (порт 8080)"""
        print("\n🔍 Тестирование HTTP Basic (порт 8080)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/http_basic.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint
            health_response = requests.get("http://localhost:8080/health", timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC
            jsonrpc_response = requests.post(
                "http://localhost:8080/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTP Basic"}, "id": 1},
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "HTTP Basic",
                "port": 8080,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ HTTP Basic: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTP Basic failed: {e}")
            return {"mode": "HTTP Basic", "success": False, "error": str(e)}
    
    def test_http_token(self) -> Dict[str, Any]:
        """Тест HTTP + Token (порт 8080)"""
        print("\n🔍 Тестирование HTTP + Token (порт 8080)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/http_token.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint с токеном
            health_response = requests.get("http://localhost:8080/health", timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC без токена (должен быть 401)
            jsonrpc_no_token = requests.post(
                "http://localhost:8080/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello"}, "id": 1},
                timeout=10
            )
            no_token_401 = jsonrpc_no_token.status_code == 401
            
            # Тест JSON-RPC с токеном
            jsonrpc_with_token = requests.post(
                "http://localhost:8080/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTP Token"}, "id": 1},
                headers={"X-API-Key": "test-token"},
                timeout=10
            )
            jsonrpc_ok = jsonrpc_with_token.status_code == 200
            
            result = {
                "mode": "HTTP + Token",
                "port": 8080,
                "health": health_ok,
                "no_token_401": no_token_401,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and no_token_401 and jsonrpc_ok
            }
            
            print(f"✅ HTTP + Token: Health={health_ok}, NoToken401={no_token_401}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTP + Token failed: {e}")
            return {"mode": "HTTP + Token", "success": False, "error": str(e)}
    
    def test_http_token_roles(self) -> Dict[str, Any]:
        """Тест HTTP + Token + Roles (порт 8080)"""
        print("\n🔍 Тестирование HTTP + Token + Roles (порт 8080)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/http_token_roles.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint
            health_response = requests.get("http://localhost:8080/health", timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC с токеном
            jsonrpc_response = requests.post(
                "http://localhost:8080/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTP Token Roles"}, "id": 1},
                headers={"X-API-Key": "test-token"},
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "HTTP + Token + Roles",
                "port": 8080,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ HTTP + Token + Roles: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTP + Token + Roles failed: {e}")
            return {"mode": "HTTP + Token + Roles", "success": False, "error": str(e)}
    
    def test_https_basic(self) -> Dict[str, Any]:
        """Тест HTTPS Basic (порт 8443)"""
        print("\n🔍 Тестирование HTTPS Basic (порт 8443)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/https_basic.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint
            health_response = requests.get("https://localhost:8443/health", verify=False, timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC
            jsonrpc_response = requests.post(
                "https://localhost:8443/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTPS Basic"}, "id": 1},
                verify=False,
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "HTTPS Basic",
                "port": 8443,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ HTTPS Basic: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTPS Basic failed: {e}")
            return {"mode": "HTTPS Basic", "success": False, "error": str(e)}
    
    def test_https_token(self) -> Dict[str, Any]:
        """Тест HTTPS + Token (порт 8443)"""
        print("\n🔍 Тестирование HTTPS + Token (порт 8443)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/https_token.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint
            health_response = requests.get("https://localhost:8443/health", verify=False, timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC с токеном
            jsonrpc_response = requests.post(
                "https://localhost:8443/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTPS Token"}, "id": 1},
                headers={"X-API-Key": "test-token"},
                verify=False,
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "HTTPS + Token",
                "port": 8443,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ HTTPS + Token: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTPS + Token failed: {e}")
            return {"mode": "HTTPS + Token", "success": False, "error": str(e)}
    
    def test_https_token_roles(self) -> Dict[str, Any]:
        """Тест HTTPS + Token + Roles (порт 8443)"""
        print("\n🔍 Тестирование HTTPS + Token + Roles (порт 8443)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/https_token_roles.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint
            health_response = requests.get("https://localhost:8443/health", verify=False, timeout=10)
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC с токеном
            jsonrpc_response = requests.post(
                "https://localhost:8443/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello HTTPS Token Roles"}, "id": 1},
                headers={"X-API-Key": "test-token"},
                verify=False,
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "HTTPS + Token + Roles",
                "port": 8443,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ HTTPS + Token + Roles: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ HTTPS + Token + Roles failed: {e}")
            return {"mode": "HTTPS + Token + Roles", "success": False, "error": str(e)}
    
    def test_mtls_basic(self) -> Dict[str, Any]:
        """Тест mTLS Basic (порт 8443)"""
        print("\n🔍 Тестирование mTLS Basic (порт 8443)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/mtls_no_roles_correct.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint с mTLS
            health_response = requests.get(
                "https://localhost:8443/health",
                verify=False,
                cert=("mtls_certificates/client/test-client.crt", "mtls_certificates/client/test-client.key"),
                timeout=10
            )
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC с mTLS
            jsonrpc_response = requests.post(
                "https://localhost:8443/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello mTLS Basic"}, "id": 1},
                verify=False,
                cert=("mtls_certificates/client/test-client.crt", "mtls_certificates/client/test-client.key"),
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "mTLS Basic",
                "port": 8443,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ mTLS Basic: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ mTLS Basic failed: {e}")
            return {"mode": "mTLS Basic", "success": False, "error": str(e)}
    
    def test_mtls_roles(self) -> Dict[str, Any]:
        """Тест mTLS + Roles (порт 8443)"""
        print("\n🔍 Тестирование mTLS + Roles (порт 8443)")
        
        try:
            # Запуск сервера
            cmd = [
                "python", "mcp_proxy_adapter/examples/full_application/main.py",
                "--config", "mcp_proxy_adapter/examples/full_application/configs/mtls_with_roles_correct.json"
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            time.sleep(12)  # Увеличиваем время ожидания
            
            # Тест health endpoint с mTLS
            health_response = requests.get(
                "https://localhost:8443/health",
                verify=False,
                cert=("mtls_certificates/client/test-client.crt", "mtls_certificates/client/test-client.key"),
                timeout=10
            )
            health_ok = health_response.status_code == 200
            
            # Тест JSON-RPC с mTLS
            jsonrpc_response = requests.post(
                "https://localhost:8443/api/jsonrpc",
                json={"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello mTLS Roles"}, "id": 1},
                verify=False,
                cert=("mtls_certificates/client/test-client.crt", "mtls_certificates/client/test-client.key"),
                timeout=10
            )
            jsonrpc_ok = jsonrpc_response.status_code == 200
            
            result = {
                "mode": "mTLS + Roles",
                "port": 8443,
                "health": health_ok,
                "jsonrpc": jsonrpc_ok,
                "success": health_ok and jsonrpc_ok
            }
            
            print(f"✅ mTLS + Roles: Health={health_ok}, JSON-RPC={jsonrpc_ok}")
            return result
            
        except Exception as e:
            print(f"❌ mTLS + Roles failed: {e}")
            return {"mode": "mTLS + Roles", "success": False, "error": str(e)}
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск полного тестирования MCP Proxy Adapter")
        print("=" * 60)
        
        # Список тестов
        tests = [
            self.test_http_basic,
            self.test_http_token,
            self.test_http_token_roles,
            self.test_https_basic,
            self.test_https_token,
            self.test_https_token_roles,
            self.test_mtls_basic,
            self.test_mtls_roles
        ]
        
        # Запуск тестов
        for test in tests:
            try:
                result = test()
                self.results.append(result)
                self.cleanup()  # Очистка после каждого теста
                time.sleep(2)  # Пауза между тестами
            except Exception as e:
                print(f"❌ Тест {test.__name__} failed: {e}")
                self.results.append({"mode": test.__name__, "success": False, "error": str(e)})
                self.cleanup()
        
        # Итоговый отчет
        self.print_summary()
    
    def print_summary(self):
        """Печать итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for result in self.results:
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            mode = result.get("mode", "Unknown")
            print(f"{status}: {mode}")
            
            if result.get("success", False):
                passed += 1
            else:
                failed += 1
                if "error" in result:
                    print(f"    Error: {result['error']}")
        
        print(f"\n🎯 РЕЗУЛЬТАТ: {passed}/{len(self.results)} тестов прошли успешно")
        
        if passed == len(self.results):
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! MCP Proxy Adapter работает корректно!")
        else:
            print(f"⚠️  {failed} тестов не прошли. Требуется доработка.")
        
        # Сохранение результатов
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Результаты сохранены в test_results.json")

def main():
    """Основная функция"""
    tester = MCPProxyTester()
    try:
        tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
