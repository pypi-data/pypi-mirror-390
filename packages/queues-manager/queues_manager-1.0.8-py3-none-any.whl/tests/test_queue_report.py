"""Agent 队列报表客户端测试用例"""
import pytest
import time
import uuid
import json
from agent_queues import AgentQueueReportClient, AgentQueueReport, QueueReport
from agent_queues import PrivateAgentTasksQueue
from agent_queues import DATA_PROCESSING, PENDING, PROCESSING, COMPLETED, FAILED


class TestAgentQueueReport:
    """Agent 队列报表客户端测试"""
    
    @pytest.fixture
    def report_client(self):
        """创建报表客户端"""
        client = AgentQueueReportClient()
        yield client
        client.close()
    
    @pytest.fixture
    def test_agents(self):
        """创建测试用的 agent IDs"""
        return [f"test_agent_{uuid.uuid4().hex[:8]}" for _ in range(3)]
    
    @pytest.fixture
    def setup_queues_with_tasks(self, test_agents):
        """设置测试队列并提交一些任务"""
        queue = PrivateAgentTasksQueue()
        try:
            # 创建队列并提交任务
            for i, agent_id in enumerate(test_agents):
                # 创建队列
                queue.create_queue(agent_id)
                
                # 提交不同状态的任务
                # Agent 0: 提交一些任务，部分完成，部分失败
                if i == 0:
                    for j in range(5):
                        submit_response = queue.submit_task(
                            agent_id=agent_id,
                            task_type=DATA_PROCESSING,
                            payload=json.dumps({"id": j}),
                            priority=5
                        )
                        if submit_response.success:
                            task_id = submit_response.task_id
                            # 获取任务并更新状态
                            get_response = queue.get_task(agent_id, timeout=1)
                            if get_response.success and get_response.task:
                                # 部分标记为完成，部分标记为失败
                                if j < 3:
                                    queue.update_task_status(
                                        task_id, agent_id, COMPLETED,
                                        result=json.dumps({"result": "success"})
                                    )
                                else:
                                    queue.update_task_status(
                                        task_id, agent_id, FAILED,
                                        error_message="Test error"
                                    )
                
                # Agent 1: 提交一些待处理任务
                elif i == 1:
                    for j in range(3):
                        queue.submit_task(
                            agent_id=agent_id,
                            task_type=DATA_PROCESSING,
                            payload=json.dumps({"id": j}),
                            priority=5
                        )
                
                # Agent 2: 提交一些处理中的任务
                elif i == 2:
                    for j in range(2):
                        submit_response = queue.submit_task(
                            agent_id=agent_id,
                            task_type=DATA_PROCESSING,
                            payload=json.dumps({"id": j}),
                            priority=5
                        )
                        if submit_response.success:
                            task_id = submit_response.task_id
                            # 获取任务并标记为处理中
                            get_response = queue.get_task(agent_id, timeout=1)
                            if get_response.success and get_response.task:
                                queue.update_task_status(
                                    task_id, agent_id, PROCESSING
                                )
            
            yield test_agents
        finally:
            queue.close()
    
    def test_get_single_agent_report(self, report_client, setup_queues_with_tasks):
        """测试获取单个 Agent 的报表"""
        agent_ids = setup_queues_with_tasks
        agent_id = agent_ids[0]
        
        try:
            report = report_client.get_single_agent_report(agent_id)
            
            assert report is not None, "报表应该存在"
            assert report.agent_id == agent_id
            assert report.queue_exists is True
            assert report.total_count >= 0
            assert report.pending_count >= 0
            assert report.processing_count >= 0
            assert report.completed_count >= 0
            assert report.failed_count >= 0
            assert 0 <= report.success_rate <= 100
            assert 0 <= report.completion_rate <= 100
            assert report.health in ["HEALTHY", "WARNING", "CRITICAL", "UNKNOWN"]
            
            print(f"✓ 单个 Agent 报表测试通过: {agent_id}")
            print(f"  任务统计: 总计={report.total_count}, "
                  f"待处理={report.pending_count}, "
                  f"处理中={report.processing_count}, "
                  f"已完成={report.completed_count}, "
                  f"失败={report.failed_count}")
            print(f"  完成情况: 成功率={report.success_rate}%, "
                  f"完成率={report.completion_rate}%")
            print(f"  健康状态: {report.health} - {report.health_message}")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_get_single_agent_report_with_details(self, report_client, setup_queues_with_tasks):
        """测试获取单个 Agent 的报表（包含任务详情）"""
        agent_ids = setup_queues_with_tasks
        agent_id = agent_ids[0]
        
        try:
            report = report_client.get_single_agent_report(
                agent_id,
                include_task_details=True
            )
            
            assert report is not None
            # 如果有任务，应该包含最近的任务列表
            if report.total_count > 0:
                assert isinstance(report.recent_tasks, list)
                assert len(report.recent_tasks) <= 10
            
            print(f"✓ 包含任务详情的报表测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_get_single_agent_report_not_exists(self, report_client):
        """测试获取不存在的 Agent 报表"""
        non_existent_agent = f"non_existent_{uuid.uuid4().hex[:8]}"
        
        try:
            report = report_client.get_single_agent_report(non_existent_agent)
            # 队列不存在时，应该返回 None
            assert report is None or report.queue_exists is False
            
            print(f"✓ 不存在的 Agent 报表测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_get_multi_agent_report(self, report_client, setup_queues_with_tasks):
        """测试获取多个 Agent 的报表"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_multi_agent_report(agent_ids)
            
            assert report is not None
            assert report.total_agents == len(agent_ids)
            assert len(report.agent_reports) <= len(agent_ids)
            assert report.total_agents >= report.active_agents
            assert report.total_tasks >= 0
            assert 0 <= report.global_success_rate <= 100
            assert 0 <= report.global_completion_rate <= 100
            
            # 验证全局统计
            total_pending = sum(r.pending_count for r in report.agent_reports)
            total_processing = sum(r.processing_count for r in report.agent_reports)
            total_completed = sum(r.completed_count for r in report.agent_reports)
            total_failed = sum(r.failed_count for r in report.agent_reports)
            
            assert report.total_pending == total_pending
            assert report.total_processing == total_processing
            assert report.total_completed == total_completed
            assert report.total_failed == total_failed
            
            print(f"✓ 多个 Agent 报表测试通过")
            print(f"  总 Agent 数: {report.total_agents}")
            print(f"  活跃 Agent: {report.active_agents}")
            print(f"  全局任务: {report.total_tasks}")
            print(f"  全局成功率: {report.global_success_rate}%")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_get_multi_agent_report_empty_list(self, report_client):
        """测试获取空 Agent 列表的报表"""
        try:
            report = report_client.get_multi_agent_report([])
            
            assert report is not None
            assert report.total_agents == 0
            assert report.active_agents == 0
            assert report.total_tasks == 0
            assert len(report.agent_reports) == 0
            
            print(f"✓ 空 Agent 列表报表测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_start_stop_monitoring(self, report_client, setup_queues_with_tasks):
        """测试开始和停止监控"""
        agent_ids = setup_queues_with_tasks
        callback_called = []
        
        def callback(report):
            callback_called.append(report)
        
        try:
            # 开始监控
            report_client.start_monitoring(
                agent_ids=agent_ids,
                update_interval=2,  # 2秒更新一次
                callback=callback
            )
            
            # 等待一段时间
            time.sleep(3)
            
            # 停止监控
            report_client.stop_monitoring()
            
            # 验证回调被调用
            assert len(callback_called) > 0, "回调应该被调用"
            
            # 验证报表内容
            for report in callback_called:
                assert report.total_agents == len(agent_ids)
                assert isinstance(report.timestamp, int)
            
            print(f"✓ 监控开始/停止测试通过，回调被调用 {len(callback_called)} 次")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_stream_reports(self, report_client, setup_queues_with_tasks):
        """测试流式获取报表"""
        agent_ids = setup_queues_with_tasks
        
        try:
            count = 0
            for report in report_client.stream_reports(
                agent_ids=agent_ids,
                update_interval=2,
                include_task_details=False
            ):
                count += 1
                assert report is not None
                assert report.total_agents == len(agent_ids)
                assert isinstance(report.timestamp, int)
                
                # 只获取前2次更新
                if count >= 2:
                    break
            
            assert count >= 1, "应该至少获取到一次报表"
            print(f"✓ 流式报表测试通过，获取了 {count} 次更新")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_report_to_dict(self, report_client, setup_queues_with_tasks):
        """测试报表转换为字典"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_multi_agent_report(agent_ids)
            
            # 转换为字典
            report_dict = report.to_dict()
            
            assert isinstance(report_dict, dict)
            assert "timestamp" in report_dict
            assert "agent_reports" in report_dict
            assert "total_agents" in report_dict
            assert "total_tasks" in report_dict
            
            # 验证 Agent 报表也可以转换
            if report.agent_reports:
                agent_dict = report.agent_reports[0].to_dict()
                assert isinstance(agent_dict, dict)
                assert "agent_id" in agent_dict
                assert "pending_count" in agent_dict
            
            print(f"✓ 报表转字典测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_get_agent_report_from_queue_report(self, report_client, setup_queues_with_tasks):
        """测试从 QueueReport 中获取指定 Agent 的报表"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_multi_agent_report(agent_ids)
            
            # 获取指定 Agent 的报表
            agent_report = report.get_agent_report(agent_ids[0])
            
            if agent_report:
                assert agent_report.agent_id == agent_ids[0]
                assert isinstance(agent_report.pending_count, int)
            else:
                # 如果队列不存在，可能返回 None
                pass
            
            print(f"✓ 从 QueueReport 获取 Agent 报表测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_health_status_detection(self, report_client, setup_queues_with_tasks):
        """测试健康状态检测"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_multi_agent_report(agent_ids)
            
            for agent_report in report.agent_reports:
                assert agent_report.health in ["HEALTHY", "WARNING", "CRITICAL", "UNKNOWN"]
                assert agent_report.health_message is not None
                
                # 验证健康状态逻辑
                if agent_report.failed_count > 0:
                    failure_rate = (agent_report.failed_count / 
                                  (agent_report.completed_count + agent_report.failed_count)) * 100
                    if failure_rate > 50:
                        assert agent_report.health == "CRITICAL"
                    elif failure_rate > 20:
                        assert agent_report.health == "WARNING"
            
            print(f"✓ 健康状态检测测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_success_rate_calculation(self, report_client, setup_queues_with_tasks):
        """测试成功率计算"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_single_agent_report(agent_ids[0])
            
            if report and report.completed_count + report.failed_count > 0:
                expected_success_rate = int(
                    (report.completed_count / 
                     (report.completed_count + report.failed_count)) * 100
                )
                assert report.success_rate == expected_success_rate
            
            print(f"✓ 成功率计算测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_completion_rate_calculation(self, report_client, setup_queues_with_tasks):
        """测试完成率计算"""
        agent_ids = setup_queues_with_tasks
        
        try:
            report = report_client.get_single_agent_report(agent_ids[0])
            
            if report and report.total_count > 0:
                total_finished = report.completed_count + report.failed_count
                expected_completion_rate = int((total_finished / report.total_count) * 100)
                assert report.completion_rate == expected_completion_rate
            
            print(f"✓ 完成率计算测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_context_manager(self, setup_queues_with_tasks):
        """测试上下文管理器"""
        agent_ids = setup_queues_with_tasks
        
        try:
            with AgentQueueReportClient() as report_client:
                report = report_client.get_multi_agent_report(agent_ids)
                assert report is not None
            
            print(f"✓ 上下文管理器测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
    
    def test_monitoring_with_different_intervals(self, report_client, setup_queues_with_tasks):
        """测试不同更新间隔的监控"""
        agent_ids = setup_queues_with_tasks
        callback_called = []
        
        def callback(report):
            callback_called.append(time.time())
        
        try:
            # 测试短间隔
            report_client.start_monitoring(
                agent_ids=agent_ids,
                update_interval=1,  # 1秒
                callback=callback
            )
            
            time.sleep(2.5)  # 等待2.5秒
            report_client.stop_monitoring()
            
            # 应该至少调用2次（0秒、1秒、2秒）
            assert len(callback_called) >= 2, f"应该至少调用2次，实际调用 {len(callback_called)} 次"
            
            print(f"✓ 不同更新间隔测试通过，调用 {len(callback_called)} 次")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

