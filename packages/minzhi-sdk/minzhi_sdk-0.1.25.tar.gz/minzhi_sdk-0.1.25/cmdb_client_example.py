#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CMDB 客户端使用示例

演示重构后的 CmdbClient 的各种功能和使用方法
"""

from minzhi.cmdb_client import CmdbClient, QueryBuilder, QueryOperation


def main():
    """主函数，演示各种使用场景"""
    
    # 初始化客户端
    client = CmdbClient(
        view_id="your_view_id",
        CMDB_SERVER="https://cmdb.example.com",
        APPID="your_app_id",
        APPSECRET="your_app_secret"
    )
    
    print("=== CMDB 客户端使用示例 ===\n")
    
    # 1. 基本查询 - 获取所有数据
    print("1. 获取所有数据")
    try:
        all_data = client.get_all_data()
        print(f"   总数据量: {len(all_data)} 条")
        if all_data:
            print(f"   第一条数据: {all_data[0]}")
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 2. 使用传统方式查询 - 单个条件
    print("2. 单条件查询（传统方式）")
    try:
        single_condition = {"key": "status", "operation": "eq", "value": "active"}
        active_data = client.get_all_data(queryKey=single_condition)
        print(f"   活跃数据量: {len(active_data)} 条")
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 3. 使用传统方式查询 - 多个条件
    print("3. 多条件查询（传统方式）")
    try:
        multiple_conditions = [
            {"key": "status", "operation": "eq", "value": "active"},
            {"key": "environment", "operation": "eq", "value": "production"}
        ]
        filtered_data = client.get_all_data(queryKey=multiple_conditions)
        print(f"   生产环境活跃数据量: {len(filtered_data)} 条")
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 4. 使用 QueryBuilder 查询（推荐方式）
    print("4. 使用 QueryBuilder 查询（推荐）")
    try:
        query = (QueryBuilder()
                 .equal("status", "active")
                 .equal("environment", "production")
                 .greater_than("createTime", "2023-01-01")
                 .build())
        
        builder_data = client.get_all_data(queryKey=query)
        print(f"   复杂查询结果: {len(builder_data)} 条")
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 5. 使用便利方法
    print("5. 使用便利方法")
    try:
        # 查找特定字段值
        servers = client.find_by_field("type", "server")
        print(f"   服务器数量: {len(servers)}")
        
        # 检查记录是否存在
        has_critical = client.exists("priority", "critical")
        print(f"   是否存在关键资产: {has_critical}")
        
        # 查找第一条记录
        first_server = client.find_one("type", "server")
        if first_server:
            print(f"   第一台服务器: {first_server.get('name', 'N/A')}")
        
        # 获取数据总数
        total_count = client.get_data_count()
        print(f"   数据总数: {total_count}")
        
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 6. 数据导入示例
    print("6. 数据导入示例")
    try:
        # 准备测试数据
        test_data = [
            {
                "name": "test-server-1",
                "ip": "192.168.1.100",
                "type": "server",
                "status": "active",
                "environment": "test"
            },
            {
                "name": "test-server-2",
                "ip": "192.168.1.101",
                "type": "server",
                "status": "active",
                "environment": "test"
            }
        ]
        
        # 单次导入
        result = client.import_data(test_data)
        print(f"   导入结果: {result}")
        
        # 多线程批量导入（适用于大量数据）
        large_data = [f"test-record-{i}" for i in range(500)]
        # 这里只是示例，实际需要构造正确的数据格式
        # success = client.thread_import_data(large_data, batch_size=50)
        # print(f"   批量导入成功: {success}")
        
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 7. 高级查询示例
    print("7. 高级查询示例")
    try:
        # 使用不同的操作符
        advanced_query = (QueryBuilder()
                         .equal("status", "active")
                         .like("name", "web%")
                         .not_equal("environment", "test")
                         .in_condition("type", ["server", "database"])
                         .less_than("cpuUsage", 80)
                         .build())
        
        advanced_result = client.get_all_data(queryKey=advanced_query)
        print(f"   高级查询结果: {len(advanced_result)} 条")
        
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 8. Token 刷新示例
    print("8. Token 刷新示例")
    try:
        new_token = client.refresh_token()
        print(f"   Token 刷新成功，新 token 长度: {len(new_token)}")
    except Exception as e:
        print(f"   错误: {e}")
    print()


def demo_query_operations():
    """演示所有支持的查询操作符"""
    print("=== 查询操作符演示 ===\n")
    
    client = CmdbClient(
        view_id="demo_view",
        CMDB_SERVER="https://cmdb.example.com",
        APPID="demo_app",
        APPSECRET="demo_secret"
    )
    
    # 演示所有操作符
    operations = [
        ("等于", QueryOperation.EQUAL.value, "status", "active"),
        ("不等于", QueryOperation.NOT_EQUAL.value, "status", "inactive"),
        ("大于", QueryOperation.GREATER_THAN.value, "createTime", "2023-01-01"),
        ("小于", QueryOperation.LESS_THAN.value, "createTime", "2024-01-01"),
        ("模糊匹配", QueryOperation.LIKE.value, "name", "server%"),
        ("包含于", QueryOperation.IN.value, "type", ["server", "database"]),
        ("非", QueryOperation.NOT.value, "deleted", True)
    ]
    
    for desc, op, field, value in operations:
        try:
            query = QueryBuilder().where(field, op, value).build()
            result = client.get_all_data(queryKey=query, pageSize=10)  # 限制结果数量
            print(f"{desc} ({op}): {len(result)} 条记录")
        except Exception as e:
            print(f"{desc} ({op}): 错误 - {e}")
    
    print()


def demo_error_handling():
    """演示错误处理"""
    print("=== 错误处理演示 ===\n")
    
    # 故意使用错误的配置
    client = CmdbClient(
        view_id="invalid_view",
        CMDB_SERVER="https://invalid.example.com",
        APPID="invalid_app",
        APPSECRET="invalid_secret"
    )
    
    try:
        # 尝试获取数据
        data = client.get_all_data()
        print(f"意外成功: {len(data)} 条记录")
    except Exception as e:
        print(f"预期的错误: {type(e).__name__}: {e}")
    
    # 演示无效查询条件
    try:
        invalid_condition = {"invalid_field": "test"}  # 缺少必需字段
        client.find_by_multiple_fields([invalid_condition])
    except Exception as e:
        print(f"查询条件验证错误: {e}")
    
    print()


if __name__ == "__main__":
    # 运行所有演示
    main()
    demo_query_operations()
    demo_error_handling()
    
    print("=== 演示完成 ===")