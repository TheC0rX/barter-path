# --- ITEM CARD
item_card-selected_item =
    <p><b>{ $icon } Selected item:</b> { $item_name }</p>

item_card-selected_offer =
    <p><b>{ $icon } Selected offer:</b> { $offer }{ $total_offers }</p>

item_card-selected_discount =
    <p><b>🎟️ Selected discount:</b> { $discount }%</p>

item_card-required_ings =
    <p><b>📋 Required resources:</b></p>

item_card-pieces =
    { $amount ->
        [one] pc.
       *[other] pcs.
    }

item_card-remains =
    <p>└ { $amount } Remaining.</p>

# --- ACTIVATING DISCOUNT
select-discount =
    <p>🎯 Select the discount you want to apply.</p>

discount-preview = 
    <p>🎟️ Preview with <b><u>{ $discount }%</u></b> discount applied.</p>

# --- RESOURCE MANAGER
select-ingredient =
    <p>🎯 Select the ingredient you want to edit.</p>

type-resources =
    <p>📝 Type the amount of resources to add them.</p>

reset-description =
    <p>🔄️ You can also reset the progress of collecting, by clicking reset button.</p>

resource-already-finished =
    <p>⚠️ The resource was already collected.</p>

must-be-number =
    <p>⚠️ Resource amount must be a number.</p>

must-be-more-zero =
    <p>⚠️ Resource amount must be greater than 0.</p>

must-be-less-limit =
    <p>⚠️ Resource amount must be less than 100 million.</p>

adding_resources-confirmation =
    <p>❓ Are you sure you want to add <b>{ $amount }</b> <b>{ $ing_name }</b> for <b>{ $item_name }</b>?</p>

reset_resources-confirmation =
    <p>❓ Are you sure you want to reset the progress of <b>{ $ing_name }</b> for <b>{ $item_name }</b>?</p>

# --- INGREDIENT CARD
ing_card-selected_item =
    <p><b>📦 Selected resource:</b> { $ing_name }</p>

ing_card-ing_progress =
    <p>{ $icon } Collected { $collected_amount } of { $required_amount } { $unit }</p>

# --- INGREDIENT FORMAT
ing_format-main_menu =
    <p>{ $icon } { $item }: { $collected_amount }/{ $required_amount } { $unit }</p>

ing_format-discount_menu =
    <p>- { $item }: <s>{ $amount }</s> { $discount_amount } { $unit }</p>

ing_format-resource_amount =
    <p>- { $item }: { $amount } { $unit }</p>