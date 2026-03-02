from wtpy import BaseSelStrategy
from wtpy import SelContext
# 导入上面定义的辅助函数或将函数内容直接放入策略方法中
# from your_module import rebalance_by_capital_percentage 

class MySelStrategy(BaseSelStrategy):
    def __init__(self, name: str, codes: list, ...):
        super().__init__(name)
        self.__codes__ = codes
        # ... 其他参数 ...

    def on_init(self, context: SelContext):
        # 订阅K线等数据
        for code in self.__codes__:
            context.stra_prepare_bars(code, "d", 1) # 准备日线数据
        context.stra_log_text("策略初始化完成")

    def on_calculate(self, context: SelContext):
        # 这是进行组合调整的时机
        # 假设您的机器学习模型已经输出了每个标的的目标资金百分比

        # 示例：假设模型决定 SHFE.rb.HOT 占 10%, SHFE.ag.HOT 占 5%
        # 您需要根据您的机器学习模型实际计算这些百分比
        ml_model_output_allocations = {
            "SHFE.rb.HOT": 0.10,
            "SHFE.ag.HOT": 0.05,
            # ... 其他可转债代码及其目标百分比 ...
        }

        # 调用我们上面定义的辅助函数进行调仓
        rebalance_by_capital_percentage(context, ml_model_output_allocations)

    def on_tick(self, context: SelContext, code: str, newTick: dict):
        # SEL策略通常不频繁处理Tick，除非有特殊高频需求
        pass

    def on_bar(self, context: SelContext, code: str, period: str, newBar: dict):
        # 如果您的调仓逻辑依赖于K线收盘，可以在这里触发 on_calculate 或直接实现调仓
        pass

