"""Agent 队列实时报表使用示例"""
import time
import json
from agent_queues import AgentQueueReportClient, create_report_client
from agent_queues import DATA_PROCESSING


def example_callback_monitoring():
    """示例1：使用回调函数监控"""
    print("=" * 60)
    print("示例1：使用回调函数实时监控")
    print("=" * 60)
    
    def on_report(report):
        """报表更新回调函数"""
        print(f"\n[报表时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp/1000))}]")
        print(f"总 Agent 数: {report.total_agents}, 活跃 Agent: {report.active_agents}")
        print(f"全局统计: 待处理={report.total_pending}, 处理中={report.total_processing}, "
              f"已完成={report.total_completed}, 失败={report.total_failed}")
        print(f"全局成功率: {report.global_success_rate}%, 完成率: {report.global_completion_rate}%")
        print("-" * 60)
        
        for agent_report in report.agent_reports:
            health_icon = {
                "HEALTHY": "✓",
                "WARNING": "⚠",
                "CRITICAL": "✗",
                "UNKNOWN": "?"
            }.get(agent_report.health, "?")
            
            print(f"{health_icon} Agent: {agent_report.agent_id}")
            print(f"  状态: {agent_report.health} - {agent_report.health_message}")
            print(f"  任务: 待处理={agent_report.pending_count}, "
                  f"处理中={agent_report.processing_count}, "
                  f"已完成={agent_report.completed_count}, "
                  f"失败={agent_report.failed_count}, "
                  f"总计={agent_report.total_count}")
            print(f"  完成情况: 成功率={agent_report.success_rate}%, "
                  f"完成率={agent_report.completion_rate}%")
            if agent_report.recent_tasks:
                print(f"  最近任务: {len(agent_report.recent_tasks)} 个")
            print()
    
    # 创建报表客户端
    report_client = AgentQueueReportClient()
    
    try:
        # 开始监控
        report_client.start_monitoring(
            agent_ids=["agent_001", "agent_002", "agent_003"],
            update_interval=5,  # 每5秒更新一次
            callback=on_report,
            include_task_details=False  # 不包含任务详情，提升性能
        )
        
        # 运行60秒
        print("开始监控，60秒后自动停止...")
        time.sleep(60)
        
    finally:
        report_client.stop_monitoring()
        report_client.close()


def example_stream_reports():
    """示例2：使用流式接口"""
    print("=" * 60)
    print("示例2：使用流式接口获取报表")
    print("=" * 60)
    
    report_client = AgentQueueReportClient()
    
    try:
        # 流式获取报表
        count = 0
        for report in report_client.stream_reports(
            agent_ids=["agent_001", "agent_002"],
            update_interval=3,  # 每3秒更新一次
            include_task_details=True  # 包含任务详情
        ):
            count += 1
            print(f"\n[第 {count} 次更新]")
            print(f"时间戳: {report.timestamp}")
            print(f"活跃 Agent: {report.active_agents}/{report.total_agents}")
            print(f"全局任务: {report.total_tasks} (待处理={report.total_pending}, "
                  f"处理中={report.total_processing}, 已完成={report.total_completed}, "
                  f"失败={report.total_failed})")
            
            # 只显示前3次更新
            if count >= 3:
                break
                
    finally:
        report_client.close()


def example_single_agent_report():
    """示例3：获取单个 Agent 的报表"""
    print("=" * 60)
    print("示例3：获取单个 Agent 的报表")
    print("=" * 60)
    
    report_client = AgentQueueReportClient()
    
    try:
        # 获取单个 Agent 的报表
        report = report_client.get_single_agent_report(
            agent_id="agent_001",
            include_task_details=True
        )
        
        if report:
            print(f"Agent ID: {report.agent_id}")
            print(f"队列存在: {report.queue_exists}")
            print(f"健康状态: {report.health} - {report.health_message}")
            print(f"任务统计:")
            print(f"  待处理: {report.pending_count}")
            print(f"  处理中: {report.processing_count}")
            print(f"  已完成: {report.completed_count}")
            print(f"  失败: {report.failed_count}")
            print(f"  总计: {report.total_count}")
            print(f"完成情况:")
            print(f"  成功率: {report.success_rate}%")
            print(f"  完成率: {report.completion_rate}%")
            
            if report.recent_tasks:
                print(f"最近任务 ({len(report.recent_tasks)} 个):")
                for task in report.recent_tasks[:5]:
                    print(f"  - {task.get('task_id', 'N/A')}: "
                          f"状态={task.get('status', 'N/A')}, "
                          f"优先级={task.get('priority', 'N/A')}")
        else:
            print("队列不存在或获取失败")
            
    finally:
        report_client.close()


def example_multi_agent_report():
    """示例4：获取多个 Agent 的报表"""
    print("=" * 60)
    print("示例4：获取多个 Agent 的报表")
    print("=" * 60)
    
    report_client = AgentQueueReportClient()
    
    try:
        # 获取多个 Agent 的报表
        report = report_client.get_multi_agent_report(
            agent_ids=["agent_001", "agent_002", "agent_003"],
            include_task_details=False
        )
        
        print(f"报表时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp/1000))}")
        print(f"总 Agent 数: {report.total_agents}")
        print(f"活跃 Agent 数: {report.active_agents}")
        print(f"\n全局统计:")
        print(f"  总任务数: {report.total_tasks}")
        print(f"  待处理: {report.total_pending}")
        print(f"  处理中: {report.total_processing}")
        print(f"  已完成: {report.total_completed}")
        print(f"  失败: {report.total_failed}")
        print(f"  全局成功率: {report.global_success_rate}%")
        print(f"  全局完成率: {report.global_completion_rate}%")
        
        print(f"\n各 Agent 详情:")
        for agent_report in report.agent_reports:
            print(f"\n  Agent: {agent_report.agent_id}")
            print(f"    健康状态: {agent_report.health}")
            print(f"    任务数: {agent_report.total_count} "
                  f"(待处理={agent_report.pending_count}, "
                  f"处理中={agent_report.processing_count}, "
                  f"已完成={agent_report.completed_count}, "
                  f"失败={agent_report.failed_count})")
            print(f"    成功率: {agent_report.success_rate}%, "
                  f"完成率: {agent_report.completion_rate}%")
            
    finally:
        report_client.close()


def example_json_output():
    """示例5：输出 JSON 格式（用于前端）"""
    print("=" * 60)
    print("示例5：输出 JSON 格式（用于前端）")
    print("=" * 60)
    
    report_client = AgentQueueReportClient()
    
    try:
        # 获取报表并转换为 JSON
        report = report_client.get_multi_agent_report(
            agent_ids=["agent_001", "agent_002"],
            include_task_details=False
        )
        
        # 转换为字典并输出 JSON
        report_dict = report.to_dict()
        json_output = json.dumps(report_dict, indent=2, ensure_ascii=False)
        print(json_output)
        
    finally:
        report_client.close()


def example_web_socket_like():
    """示例6：模拟 WebSocket 实时推送（用于前端集成）"""
    print("=" * 60)
    print("示例6：模拟 WebSocket 实时推送")
    print("=" * 60)
    
    report_client = AgentQueueReportClient()
    
    def send_to_frontend(report):
        """模拟发送到前端"""
        # 这里可以转换为 WebSocket 消息、SSE 事件等
        data = {
            "type": "queue_report",
            "timestamp": report.timestamp,
            "data": report.to_dict()
        }
        # 实际应用中，这里会通过 WebSocket 发送
        print(f"[WebSocket] 发送报表: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        # 开始监控并实时推送
        report_client.start_monitoring(
            agent_ids=["agent_001", "agent_002"],
            update_interval=5,
            callback=send_to_frontend
        )
        
        # 运行一段时间
        time.sleep(30)
        
    finally:
        report_client.stop_monitoring()
        report_client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            "1": example_callback_monitoring,
            "2": example_stream_reports,
            "3": example_single_agent_report,
            "4": example_multi_agent_report,
            "5": example_json_output,
            "6": example_web_socket_like
        }
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"未知示例编号: {example_num}")
            print("可用示例: 1-6")
    else:
        print("请指定示例编号 (1-6)")
        print("1: 回调函数监控")
        print("2: 流式接口")
        print("3: 单个 Agent 报表")
        print("4: 多个 Agent 报表")
        print("5: JSON 输出")
        print("6: WebSocket 模拟")

