from wtpy import SelContext
from wtpy.ProductMgr import ProductInfo

def rebalance_by_capital_percentage(
    context: SelContext,
    target_allocations: dict[str, float]  # 例如: {"SHFE.rb.HOT": 0.1, "SHFE.ag.HOT": 0.05}
):
    """
    根据总资金百分比进行多标的调仓。

    参数:
    context: SelContext实例，策略上下文。
    target_allocations: 字典，键为标的代码(stdCode)，值为该标的占总资金的目标百分比。
                        所有百分比之和不应超过1.0。
    """

    # 1. 获取总资金 (包括可用资金和当前持仓总市值)
    # total_balance: 动态权益 (动态权益 = 总平仓盈亏 + 总浮动盈亏 + 初始资金 - 总手续费)
    # 这里的 total_balance 是一个简化，可能需要根据您的实际资金管理逻辑进行调整
    # 例如，您可以考虑使用 context.stra_get_fund_data(0) 获取动态权益
    total_capital = context.stra_get_fund_data(0) # 0 for dynamic equity

    if total_capital <= 0:
        context.stra_log_text("当前总资金为零或负数，无法进行调仓。", level=2)
        return

    context.stra_log_text(f"当前总资金: {total_capital:.2f}")

    # 遍历每个目标分配
    for std_code, target_percentage in target_allocations.items():
        if target_percentage < 0:
            context.stra_log_text(f"标的 {std_code} 的目标百分比不能为负，跳过。", level=2)
            continue

        # 2. 获取标的当前价格和产品信息
        current_price = context.stra_get_price(std_code)
        if current_price <= 0:
            context.stra_log_text(f"无法获取标的 {std_code} 的当前价格，跳过调仓。", level=2)
            continue
        
        # 获取产品信息以获取交易乘数和最小交易单位
        product_info: ProductInfo = context.stra_get_comminfo(std_code)
        if product_info is None:
            context.stra_log_text(f"无法获取标的 {std_code} 的产品信息，跳过调仓。", level=2)
            continue

        volume_scale = product_info.volscale # 数量乘数，如期货的1手=10吨，股票的1手=100股
        price_tick = product_info.pricetick # 价格最小变动单位
        min_lots = product_info.minlots # 最小交易数量

        # 3. 计算目标金额和目标数量
        target_value = total_capital * target_percentage
        
        # 计算理论上的目标数量
        # 对于期货，qty = 目标金额 / (当前价格 * 数量乘数)
        # 对于股票，qty = 目标金额 / (当前价格 * 100) (如果product_info.volscale是1)
        # 确保计算考虑了 volscale，因为下单通常是按“手数”或“股”
        
        # 如果是股票，volscale通常是1，但下单需要考虑100股的单位
        # 这里需要更精细的逻辑来区分股票和期货，并处理交易单位
        # 暂时简化处理，假设 product_info.volscale 可以正确地表示一个“单位”的价值乘数
        
        target_qty_raw = target_value / (current_price * volume_scale) if volume_scale > 0 else 0

        # 根据最小交易数量 (min_lots 或 lotstick) 进行数量调整
        # 例如，股票通常是100股的整数倍，期货是1手的整数倍
        if target_qty_raw < min_lots:
            target_qty = 0 # 小于最小交易数量则不交易
        else:
            # 向下取整到最小交易单位的整数倍，避免超限
            target_qty = (target_qty_raw // min_lots) * min_lots 
        
        # 获取当前持仓
        current_pos = context.stra_get_position(std_code)

        # 仅当目标数量与当前持仓有显著差异时才调仓
        if abs(target_qty - current_pos) >= min_lots: # 假设min_lots是最小调仓单位
            # 4. 调整仓位
            context.stra_set_position(std_code, target_qty, f"rebal_pct_{target_percentage*100:.0f}%")
            context.stra_log_text(
                f"对标的 {std_code} 进行调仓：当前价格 {current_price:.2f}, "
                f"总资金 {total_capital:.2f}, 目标百分比 {target_percentage*100:.2f}%, "
                f"目标金额 {target_value:.2f}, 目标数量 {target_qty}, 当前持仓 {current_pos}"
            )
        else:
            context.stra_log_text(
                f"标的 {std_code} 持仓接近目标数量 {target_qty} (当前 {current_pos}), 无需调仓。"
            )


