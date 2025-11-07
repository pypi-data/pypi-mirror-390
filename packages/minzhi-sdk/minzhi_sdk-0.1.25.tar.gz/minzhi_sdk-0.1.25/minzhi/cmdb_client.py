from typing import Any, Dict, List, Union, Optional
from loguru import logger
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from enum import Enum

requests.packages.urllib3.disable_warnings()


class QueryOperation(Enum):
    """查询操作符枚举"""
    EQUAL = "eq"           # 等于
    LIKE = "lk"            # 模糊匹配
    GREATER_THAN = "gt"    # 大于
    LESS_THAN = "lt"       # 小于
    NOT_EQUAL = "ne"       # 不等于
    NOT = "not"            # 非
    IN = "in"              # 包含于
    
    @classmethod
    def get_all_operations(cls):
        """获取所有支持的操作符"""
        return [op.value for op in cls]
    
    @classmethod
    def is_valid_operation(cls, operation: str) -> bool:
        """验证操作符是否有效"""
        return operation in cls.get_all_operations()


class QueryConditionValidator:
    """查询条件验证器"""
    
    REQUIRED_FIELDS = ["key", "operation", "value"]
    
    @classmethod
    def validate_condition(cls, condition: Dict[str, Any]) -> bool:
        """验证单个查询条件"""
        if not isinstance(condition, dict):
            logger.error(f"查询条件必须是字典类型，实际类型: {type(condition)}")
            return False
        
        # 检查必需字段
        for field in cls.REQUIRED_FIELDS:
            if field not in condition:
                logger.error(f"查询条件缺少必需字段: {field}")
                return False
        
        # 验证操作符
        operation = condition.get("operation")
        if not QueryOperation.is_valid_operation(operation):
            logger.error(f"无效的操作符: {operation}，支持的操作符: {QueryOperation.get_all_operations()}")
            return False
        
        return True
    
    @classmethod
    def validate_conditions(cls, conditions: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """验证并标准化查询条件列表"""
        if conditions is None:
            return []
        
        # 统一转换为列表格式
        if isinstance(conditions, dict):
            conditions = [conditions]
        elif not isinstance(conditions, list):
            logger.error(f"查询条件格式错误，应为字典或列表，实际类型: {type(conditions)}")
            return []
        
        # 验证每个条件
        valid_conditions = []
        for i, condition in enumerate(conditions):
            if cls.validate_condition(condition):
                valid_conditions.append(condition)
            else:
                logger.warning(f"跳过无效的查询条件 [{i}]: {condition}")
        
        return valid_conditions


class QueryBuilder:
    """查询条件构建器"""
    
    def __init__(self):
        self.conditions: List[Dict[str, Any]] = []
    
    def where(self, key: str, operation: str, value: Any) -> 'QueryBuilder':
        """添加查询条件"""
        if QueryOperation.is_valid_operation(operation):
            self.conditions.append({
                "key": key,
                "operation": operation,
                "value": value
            })
        else:
            logger.error(f"无效的操作符: {operation}")
        return self
    
    def equal(self, key: str, value: Any) -> 'QueryBuilder':
        """等于条件"""
        return self.where(key, QueryOperation.EQUAL.value, value)
    
    def like(self, key: str, value: Any) -> 'QueryBuilder':
        """模糊匹配条件"""
        return self.where(key, QueryOperation.LIKE.value, value)
    
    def greater_than(self, key: str, value: Any) -> 'QueryBuilder':
        """大于条件"""
        return self.where(key, QueryOperation.GREATER_THAN.value, value)
    
    def less_than(self, key: str, value: Any) -> 'QueryBuilder':
        """小于条件"""
        return self.where(key, QueryOperation.LESS_THAN.value, value)
    
    def not_equal(self, key: str, value: Any) -> 'QueryBuilder':
        """不等于条件"""
        return self.where(key, QueryOperation.NOT_EQUAL.value, value)
    
    def not_condition(self, key: str, value: Any) -> 'QueryBuilder':
        """非条件"""
        return self.where(key, QueryOperation.NOT.value, value)
    
    def in_condition(self, key: str, value: Any) -> 'QueryBuilder':
        """包含条件"""
        return self.where(key, QueryOperation.IN.value, value)
    
    def build(self) -> List[Dict[str, Any]]:
        """构建查询条件列表"""
        return self.conditions.copy()
    
    def clear(self) -> 'QueryBuilder':
        """清空查询条件"""
        self.conditions.clear()
        return self


class CmdbClient:
    """
    CMDB (配置管理数据库) 客户端
    
    提供与 CMDB 系统交互的功能，包括数据查询、导入和多线程批量操作。
    
    Attributes:
        SERVER (str): CMDB 服务器地址
        appid (str): 应用 ID
        appSecret (str): 应用密钥
        view_id (str): 视图 ID（连接器 ID）
        HEADERS (dict): 包含认证信息的请求头
    
    Example:
        >>> client = CmdbClient(
        ...     view_id="your_view_id",
        ...     CMDB_SERVER="https://cmdb.example.com",
        ...     APPID="your_app_id",
        ...     APPSECRET="your_app_secret"
        ... )
        >>>
        >>> # 使用 QueryBuilder 构建查询条件
        >>> query = QueryBuilder().equal("status", "active").build()
        >>> data = client.get_all_data(queryKey=query)
        >>>
        >>> # 导入数据
        >>> import_data = [{"name": "server1", "ip": "192.168.1.1"}]
        >>> result = client.import_data(import_data)
    """
    def __init__(self, view_id: str, CMDB_SERVER: str, APPID: str, APPSECRET: str):
        """
        初始化 CMDB 客户端
        
        Args:
            view_id: 视图 ID（连接器 ID）
            CMDB_SERVER: CMDB 服务器地址
            APPID: 应用 ID
            APPSECRET: 应用密钥
        """
        self.SERVER = CMDB_SERVER
        self.appid = APPID
        self.appSecret = APPSECRET
        self.view_id = view_id
        self.HEADERS = {
            "Authorization": self.get_token()
        }

    @logger.catch
    def get_token(self) -> str:
        """
        获取 token
        
        Returns:
            str: 认证 token
        """
        url = f"{self.SERVER}/api/v2/auth/login"
        data = {
            "appId": self.appid,
            "appSecret": self.appSecret
        }
        logger.debug(f"CmdbAPI -> get_token url: {url}")
        logger.debug(f"CmdbAPI -> get_token data: {json.dumps(data)}")
        
        try:
            response = requests.post(url=url, json=data, verify=False)
            response.raise_for_status()
            response_json = response.json()
            logger.debug(f"CmdbAPI -> get_token Res: {json.dumps(response_json)}")
            
            token = response_json.get('Authorization')
            if not token:
                logger.error("获取 token 失败：响应中未找到 Authorization 字段")
                raise ValueError("获取 token 失败")
            
            return token
        except requests.exceptions.RequestException as e:
            logger.error(f"获取 token 请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"获取 token 响应解析失败: {e}")
            raise

    @logger.catch
    def get_all_data(self,
                    startPage: int = 1,
                    pageSize: int = 1000,
                    queryKey: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
        """
        获取所有数据
        
        Args:
            startPage: 起始页码，默认为 1
            pageSize: 每页大小，默认为 1000
            queryKey: 查询条件，支持以下格式：
                    - 单个条件: {"key": "status", "operation": "eq", "value": "active"}
                    - 多个条件: [{"key": "status", "operation": "eq", "value": "active"}, ...]
                    - 使用 QueryBuilder: QueryBuilder().equal("status", "active").build()
        
        Returns:
            List[Dict[str, Any]]: 查询结果数据列表
        """
        url = f"{self.SERVER}/api/v2/data/view"
        
        # 验证和标准化查询条件
        queryCondition = QueryConditionValidator.validate_conditions(queryKey)
        
        logger.debug(f"CmdbAPI -> get_all_data url: {url}")
        logger.debug(f"CmdbAPI -> get_all_data headers: {self.HEADERS}")
        logger.debug(f"CmdbAPI -> get_all_data query conditions: {json.dumps(queryCondition, ensure_ascii=False)}")
        
        data = {
            "moduleName": "",
            "name": "",
            "pageSize": pageSize,
            "queryCondition": queryCondition,
            "startPage": startPage,
            "viewid": self.view_id
        }
        
        logger.debug(f"CmdbAPI -> get_all_data request data: {json.dumps(data, ensure_ascii=False)}")
        
        response_data = []
        current_page = startPage
        
        while True:
            try:
                response = requests.post(url=url, headers=self.HEADERS, json=data, verify=False)
                response.raise_for_status()  # 检查 HTTP 状态码
                response_json = response.json()
                
                total = response_json.get("total", 0)
                content = response_json.get("content", [])
                
                if not content:
                    logger.debug(f"第 {current_page} 页无数据，停止查询")
                    break
                    
                response_data.extend(content)
                logger.debug(f"第 {current_page} 页获取 {len(content)} 条数据，累计 {len(response_data)}/{total}")
                
                if len(response_data) >= total:
                    logger.debug(f"数据获取完成，总计 {len(response_data)} 条记录")
                    break
                    
                current_page += 1
                data['startPage'] = current_page
                
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败，页码: {current_page}, 错误: {e}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"响应解析失败，页码: {current_page}, 错误: {e}")
                break
            except Exception as e:
                logger.error(f"未知错误，页码: {current_page}, 错误: {e}")
                break
        
        logger.debug(f"CmdbAPI -> get_all_data 最终结果: {len(response_data)} 条记录")
        return response_data

    @logger.catch
    def import_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        导入数据
        
        Args:
            data: 要导入的数据列表
            
        Returns:
            Dict[str, Any]: 导入结果响应
        """
        if not data:
            logger.warning("导入数据为空")
            return {"success": False, "message": "导入数据为空"}
        
        url = f"{self.SERVER}/api/v2/data/storage"
        logger.debug(f"CmdbAPI -> import_data url: {url}")
        logger.debug(f"CmdbAPI -> import_data headers: {self.HEADERS}")
        
        request_data = {
            "mid": self.view_id,
            "data": data
        }
        logger.debug(f"CmdbAPI -> import_data data: {json.dumps(request_data, ensure_ascii=False)}")
        
        try:
            response = requests.post(url=url, headers=self.HEADERS, json=request_data, verify=False)
            response.raise_for_status()
            response_json = response.json()
            logger.debug(f"CmdbAPI -> import_data Res: {json.dumps(response_json, ensure_ascii=False)}")
            return response_json
        except requests.exceptions.RequestException as e:
            logger.error(f"导入数据请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"导入数据响应解析失败: {e}")
            raise
    
    @logger.catch
    def thread_import_data(self, data: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """
        多线程导入数据
        
        Args:
            data: 要导入的数据列表
            batch_size: 每批数据大小，默认为 100
            
        Returns:
            bool: 是否全部导入成功
        """
        if not data:
            logger.warning("导入数据为空")
            return False
        
        logger.info(f"开始多线程导入数据，总数据量: {len(data)}, 批量大小: {batch_size}")
        
        success_count = 0
        total_batches = (len(data) + batch_size - 1) // batch_size
        
        with ThreadPoolExecutor(max_workers=min(cpu_count(), total_batches)) as executor:
            futures = []
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i+batch_size]
                future = executor.submit(self._import_batch_with_retry, batch_data, i // batch_size + 1)
                futures.append(future)
            
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    if result.get("success", False):
                        success_count += 1
                        logger.debug(f"批次 {i+1} 导入成功")
                    else:
                        logger.error(f"批次 {i+1} 导入失败: {result.get('message', '未知错误')}")
                except Exception as e:
                    logger.error(f"批次 {i+1} 导入异常: {e}")
        
        logger.info(f"多线程导入完成，成功批次: {success_count}/{total_batches}")
        return success_count == total_batches
    
    def _import_batch_with_retry(self, batch_data: List[Dict[str, Any]], batch_num: int, max_retries: int = 3) -> Dict[str, Any]:
        """
        带重试机制的批量导入
        
        Args:
            batch_data: 批量数据
            batch_num: 批次编号
            max_retries: 最大重试次数
            
        Returns:
            Dict[str, Any]: 导入结果
        """
        for attempt in range(max_retries):
            try:
                result = self.import_data(batch_data)
                logger.debug(f"批次 {batch_num} 第 {attempt + 1} 次尝试成功")
                return result
            except Exception as e:
                logger.warning(f"批次 {batch_num} 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"批次 {batch_num} 所有重试均失败")
                    return {"success": False, "message": f"重试 {max_retries} 次后仍然失败: {e}"}

    
    # 便利方法
    
    def find_by_field(self, field_name: str, value: Any, operation: str = "eq") -> List[Dict[str, Any]]:
        """
        根据字段值查找数据
        
        Args:
            field_name: 字段名
            value: 字段值
            operation: 操作符，默认为 "eq"
            
        Returns:
            List[Dict[str, Any]]: 匹配的数据列表
        """
        condition = {"key": field_name, "operation": operation, "value": value}
        return self.get_all_data(queryKey=condition)
    
    def find_by_multiple_fields(self, conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据多个字段条件查找数据
        
        Args:
            conditions: 查询条件列表，格式: [{"key": "field1", "operation": "eq", "value": "value1"}, ...]
            
        Returns:
            List[Dict[str, Any]]: 匹配的数据列表
        """
        return self.get_all_data(queryKey=conditions)
    
    def get_data_count(self, queryKey: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None) -> int:
        """
        获取数据总数
        
        Args:
            queryKey: 查询条件
            
        Returns:
            int: 数据总数
        """
        # 使用 pageSize=1 只获取第一页来获取总数
        result = self.get_all_data(startPage=1, pageSize=1, queryKey=queryKey)
        return len(result)
    
    def exists(self, field_name: str, value: Any, operation: str = "eq") -> bool:
        """
        检查是否存在符合条件的记录
        
        Args:
            field_name: 字段名
            value: 字段值
            operation: 操作符，默认为 "eq"
            
        Returns:
            bool: 是否存在记录
        """
        data = self.find_by_field(field_name, value, operation)
        return len(data) > 0
    
    def find_one(self, field_name: str, value: Any, operation: str = "eq") -> Optional[Dict[str, Any]]:
        """
        查找第一条符合条件的记录
        
        Args:
            field_name: 字段名
            value: 字段值
            operation: 操作符，默认为 "eq"
            
        Returns:
            Optional[Dict[str, Any]]: 第一条匹配的记录，如果没有则返回 None
        """
        data = self.find_by_field(field_name, value, operation)
        return data[0] if data else None
    
    def refresh_token(self) -> str:
        """
        刷新认证 token
        
        Returns:
            str: 新的 token
        """
        new_token = self.get_token()
        self.HEADERS["Authorization"] = new_token
        logger.info("Token 刷新成功")
        return new_token
