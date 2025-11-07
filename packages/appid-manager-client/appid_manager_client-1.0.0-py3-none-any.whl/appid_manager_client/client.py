"""
AppID客户端SDK
提供AppID的获取和释放功能，支持轮询等待
"""
import time
import requests
from typing import Tuple, Optional, Dict, Any


class AppIdClient:
    """AppID客户端"""
    
    def __init__(self, base_url: str, auth_token: str, product_name: Optional[str] = None, timeout: int = 5):
        """
        初始化AppID客户端
        
        Args:
            base_url: 服务端地址（必填）
            auth_token: 认证token（必填）
            product_name: 产品名称，如果指定则在调用时自动使用（可选）
            timeout: 请求超时时间（秒），默认5秒
        """
        if not base_url or not auth_token:
            raise ValueError("base_url and auth_token are required")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth_token = auth_token
        self.product_name = product_name  # 保存默认的产品名称
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头（包含认证信息）"""
        headers = {}
        if self.auth_token:
            # 使用 X-API-Key header
            headers['X-API-Key'] = self.auth_token
        return headers
    
    def acquire_appid(self, product_name: Optional[str] = None, max_retries: int = 60, retry_interval: int = 60) -> Tuple[str, int, int, str]:
        """
        获取可用的AppID，支持轮询等待
        
        Args:
            product_name: 产品名称，用于隔离不同业务的AppID（可选）
                        如果未指定，使用初始化时的 product_name
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            
        Returns:
            (appid, vid, starttime, productName): AppID、VID、开始时间和产品名称
            
        Raises:
            Exception: 获取失败或超时
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
            
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/appid/acquire",
                    json={"productName": product_name},
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    # 成功获取
                    data = response.json()
                    return data["appid"], data["vid"], data["starttime"], data["productName"]
                
                elif response.status_code == 202:
                    # 需要等待
                    data = response.json()
                    error = data.get("error")
                    retry_after = data.get("retry_after", retry_interval)
                    message = data.get("message", "Waiting for available appid")
                    
                    print(f"[Attempt {attempt + 1}/{max_retries}] {message}")
                    
                    if error == "no_available":
                        # 所有AppID都不可用，等待到下个小时
                        print(f"All appids for product '{product_name}' are in use for current hour, waiting {retry_after}s...")
                        time.sleep(retry_after)
                    elif error == "waiting":
                        # 服务端正在等待，客户端也等待
                        print(f"All appids for product '{product_name}' are in use, retrying in {retry_after}s...")
                        time.sleep(retry_after)
                    else:
                        print(f"Unknown error: {error}, retrying in {retry_after}s...")
                        time.sleep(retry_after)
                
                elif response.status_code == 401:
                    # 认证失败
                    data = response.json()
                    error_msg = data.get("message", "Authentication failed")
                    raise Exception(f"Authentication failed: {error_msg}")
                
                else:
                    # 其他错误
                    print(f"HTTP {response.status_code}: {response.text}")
                    time.sleep(retry_interval)
            
            except requests.exceptions.Timeout:
                print(f"[Attempt {attempt + 1}/{max_retries}] Request timeout, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            
            except requests.exceptions.ConnectionError as e:
                print(f"[Attempt {attempt + 1}/{max_retries}] Connection error, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            
            except Exception as e:
                print(f"[Attempt {attempt + 1}/{max_retries}] Unexpected error: {e}, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
        
        raise Exception(f"Failed to acquire appid after {max_retries} attempts")
    
    def release_appid(self, appid: str, product_name: Optional[str] = None) -> bool:
        """
        释放AppID
        
        Args:
            appid: 要释放的AppID
            product_name: 产品名称，用于验证AppID归属（可选）
                        如果未指定，使用初始化时的 product_name
            
        Returns:
            bool: 是否成功释放
            
        Raises:
            Exception: 释放失败
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
            
        try:
            response = requests.post(
                f"{self.base_url}/api/appid/release",
                json={"appid": appid, "productName": product_name},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"AppID {appid} for product '{product_name}' released successfully at {data.get('stoptime')}")
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to release AppID {appid} for product '{product_name}': {error_msg}")
                raise Exception(f"Release failed: {error_msg}")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timeout while releasing AppID")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error while releasing AppID")
        except Exception as e:
            raise Exception(f"Unexpected error while releasing AppID: {e}")
    
    def get_status(self, product_name: Optional[str] = None) -> Optional[dict]:
        """
        获取AppID状态统计
        
        Args:
            product_name: 产品名称，如果指定则只统计该产品的AppID（可选）
                        如果未指定且初始化时设置了 product_name，则使用默认值
                        如果为 None，则获取所有产品的状态
            
        Returns:
            dict: 状态信息，失败时返回None
        """
        try:
            params = {}
            # 如果传入了 product_name，使用传入的值
            # 如果未传入但初始化时设置了 product_name，使用默认值
            # 如果都为 None，则不传参数（获取所有产品状态）
            if product_name:
                params['productName'] = product_name
            elif self.product_name:
                params['productName'] = self.product_name
            
            response = requests.get(
                f"{self.base_url}/api/appid/status",
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get status: HTTP {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print("Request timeout while getting status")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error while getting status")
            return None
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    def init_product(self, product_name: Optional[str] = None, appIds: Optional[Dict[str, str]] = None) -> bool:
        """
        初始化或重置产品AppID配置
        
        Args:
            product_name: 产品名称（可选）
                        如果未指定，使用初始化时的 product_name
            appIds: AppID配置 {appid: vid}（可选）
                   如果未指定且初始化时设置了 product_name，则不传此参数
            
        Returns:
            bool: 是否成功初始化
            
        Raises:
            Exception: 初始化失败
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
        
        if appIds is None:
            raise ValueError("appids is required")
        try:
            response = requests.post(
                f"{self.base_url}/api/appid/init",
                json={"productName": product_name, "appIds": appIds},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Product '{product_name}' initialized successfully: {data.get('message')}")
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to initialize product '{product_name}': {error_msg}")
                raise Exception(f"Initialization failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            raise Exception("Request timeout while initializing product")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error while initializing product")
        except Exception as e:
            raise Exception(f"Unexpected error while initializing product: {e}")

    def store_test_result(self, product_name: str, session_id: str, test_data: Dict[str, Any]) -> bool:
        """
        存储测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型）
            session_id: 测试会话ID（用于区分不同的测试会话，如pytest worker进程）
            test_data: 测试用例数据字典
            
        Returns:
            bool: 是否成功存储
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/test/result",
                json={
                    "product_name": product_name,
                    "session_id": session_id,
                    "test_data": test_data
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to store test result: {error_msg}")
                return False
        except Exception as e:
            print(f"Error storing test result: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False

