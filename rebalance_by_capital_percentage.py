from wtpy import SelContext
from wtpy.ProductMgr import ProductInfo

def rebalance_by_capital_percentage(
    context: SelContext,
    target_allocations: dict[str, dict]  # 例如: {"SHFE.rb.HOT": {"percentage": 0.1, "stopprice": 3500.0}}
):
    """
    根据总资金百分比进行多标的调仓，并支持设置止损价格。

    参数:
    context: SelContext实例，策略上下文。
    target_allocations: 字典，键为标的代码(stdCode)，值为包含 'percentage' 和 'stopprice' 的字典。
                        'percentage' 为该标的占总资金的目标百分比。
                        'stopprice' 为该标的的止损价格（绝对价格）。
                        所有百分比之和不应超过1.0。
    """

    total_capital = context.stra_get_fund_data(0) # 0 for dynamic equity

    if total_capital <= 0:
        context.stra_log_text("当前总资金为零或负数，无法进行调仓。", level=2)
        return

    context.stra_log_text(f"当前总资金: {total_capital:.2f}")

    for std_code, alloc_info in target_allocations.items():
        target_percentage = alloc_info.get("percentage", 0.0)
        stopprice = alloc_info.get("stopprice", 0.0) # 获取止损价格

        if target_percentage < 0:
            context.stra_log_text(f"标的 {std_code} 的目标百分比不能为负，跳过。", level=2)
            continue

        current_price = context.stra_get_price(std_code)
        if current_price <= 0:
            context.stra_log_text(f"无法获取标的 {std_code} 的当前价格，跳过调仓。", level=2)
            continue
        
        product_info: ProductInfo = context.stra_get_comminfo(std_code)
        if product_info is None:
            context.stra_log_text(f"无法获取标的 {std_code} 的产品信息，跳过调仓。", level=2)
            continue

        volume_scale = product_info.volscale
        price_tick = product_info.pricetick
        min_lots = product_info.minlots

        target_value = total_capital * target_percentage
        
        target_qty_raw = target_value / (current_price * volume_scale) if volume_scale > 0 else 0

        if target_qty_raw < min_lots:
            target_qty = 0
        else:
            target_qty = (target_qty_raw // min_lots) * min_lots 
        
        current_pos = context.stra_get_position(std_code)

        # 仅当目标数量与当前持仓有显著差异时才调仓
        if abs(target_qty - current_pos) >= min_lots:
            # 调整仓位，并传入止损价格
            context.stra_set_position(std_code, target_qty, f"rebal_pct_{target_percentage*100:.0f}%", stopprice=stopprice)
            context.stra_log_text(
                f"对标的 {std_code} 进行调仓：当前价格 {current_price:.2f}, "
                f"总资金 {total_capital:.2f}, 目标百分比 {target_percentage*100:.2f}%, "
                f"目标金额 {target_value:.2f}, 目标数量 {target_qty}, 当前持仓 {current_pos}, "
                f"止损价 {stopprice:.2f}"
            )
        else:
            context.stra_log_text(
                f"标的 {std_code} 持仓接近目标数量 {target_qty} (当前 {current_pos}), 无需调仓。"
            )


