import time
from dataclasses import dataclass

from snailjob import *


@job("testJobExecutor")
def test_job_executor(args: JobArgs) -> ExecuteResult:
    SnailLog.REMOTE.info(f"job_params: {args.job_params}")

    # 执行一个超过40秒的任务，如果中间第30秒可以正常发送心跳，说明任务执行不阻塞
    for i in range(40):
        SnailLog.REMOTE.info(f"loop {i}")
        if ThreadPoolCache.event_is_set(args.task_batch_id):
            SnailLog.REMOTE.info("任务已经被中断，立即返回")
            return ExecuteResult.failure()
        time.sleep(1)

    SnailLog.REMOTE.info("sync job1 done")
    return ExecuteResult.success()


@job("testJobExecutorFailed")
def test_job_executor_failed(args: JobArgs):
    SnailLog.LOCAL.info("testJobExecutorFailed, SnailJobError raised")
    raise SnailJobError("这是故意抛出的异常")


@job("testWorkflowAnnoJobExecutor1")
def testWorkflowAnnoJobExecutor1(args: JobArgs) -> ExecuteResult:
    @dataclass
    class FailOrderPo:
        orderId: str = None

    order = FailOrderPo()
    order.orderId = "dhb52"
    SnailLog.REMOTE.info(f"job_params: {args.job_params}")
    args.append_context("name", "testWorkflowAnnoJobExecutor")
    return ExecuteResult.success(order)


@job("testWorkflowAnnoJobExecutor2")
def testWorkflowAnnoJobExecutor2(args: JobArgs) -> ExecuteResult:
    SnailLog.LOCAL.info(f"Name: {args.get_wf_context('name')}")
    return ExecuteResult.success()


testMyMapExecutor = MapExecutor("testMyMapExecutor")


@testMyMapExecutor.map()
def testMyMapExecutor_rootMap(args: MapArgs):
    assert args.task_name == ROOT_MAP
    return mr_do_map(["1", "2", "3", "4"], "TWO_MAP")


@testMyMapExecutor.map("TWO_MAP")
def testMyMapExecutor_twoMap(args: MapArgs):
    return ExecuteResult.success(args.map_result)


testAnnoMapJobExecutor = MapReduceExecutor("testAnnoMapJobExecutor")


@testAnnoMapJobExecutor.map()
def testAnnoMapJobExecutor_rootMap(args: MapArgs) -> ExecuteResult:
    print(args)
    args.append_context("Month", "2023-01")
    return mr_do_map(["1", "2", "3"], "MONTH_MAP")


@testAnnoMapJobExecutor.map("MONTH_MAP")
def testAnnoMapJobExecutor_monthMap(args: MapArgs) -> ExecuteResult:
    print("MONTH_MAP called")
    args.append_context("Month", "2023-01")
    print(f"type(args) = {type(args)}, {args}")
    return ExecuteResult.success([1, 2])


@testAnnoMapJobExecutor.reduce()
def testAnnoMapJobExecutor_reduce(args: ReduceArgs) -> ExecuteResult:
    print("reduce called")
    print(f"type(args) = {type(args)}, {args}")
    return ExecuteResult.success([[3, 4], [5, 6]])


@testAnnoMapJobExecutor.merge()
def testAnnoMapJobExecutor_merge(args: MergeReduceArgs) -> ExecuteResult:
    print("merge reduce called")
    print(f"type(args) = {type(args)}, {args}")
    return ExecuteResult.success([3, 4])


testAnnoMapReduceJobExecutor = MapReduceExecutor("testAnnoMapReduceJobExecutor")


@testAnnoMapReduceJobExecutor.map()
def testAnnoMapReduceJobExecutor_rootMap(args: MapArgs):
    return mr_do_map(["1", "2", "3", "4", "5", "6"], "MONTH_MAP")


@testAnnoMapReduceJobExecutor.map("MONTH_MAP")
def testAnnoMapReduceJobExecutor_monthMap(args: MapArgs):
    return ExecuteResult.success(int(args.map_result) * 2)


@testAnnoMapReduceJobExecutor.reduce()
def testAnnoMapReduceJobExecutor_reduce(args: ReduceArgs):
    return ExecuteResult.success(sum([int(x) for x in args.map_result]))


@testAnnoMapReduceJobExecutor.merge()
def testAnnoMapReduceJobExecutor_merge(args: MergeReduceArgs):
    return ExecuteResult.success(sum([int(x) for x in args.reduces]))
