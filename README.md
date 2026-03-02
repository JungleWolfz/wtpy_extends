为SEL引擎提供一个按总资金百分比多标的调仓函数是一个很好的想法，可以简化资金管理逻辑。由于WonderTrader框架本身是基于数量进行仓位管理的，我们可以在策略层面封装这个功能，而不是修改引擎的底层API。

我们可以设计一个辅助函数（或者集成到您自定义的 BaseSelStrategy 中），它负责计算每个标的应持有的具体数量，然后调用 [context.stra_set_position](%2Fwondertrader%2Fwtpy%2Fwtpy%2FCtaContext.py#L319) 来实际调整仓位。

核心思路：

获取总资金： 包括可用资金和当前持仓的总市值。

计算目标金额： 根据每个标的的目标百分比和总资金，计算出该标的应持有的目标金额。
计算目标数量： 根据目标金额和标的当前价格、交易单位，计算出应持有的具体数量。
调整仓位： 调用 [context.stra_set_position](%2Fwondertrader%2Fwtpy%2Fwtpy%2FCtaContext.py#L319) 完成调仓。
