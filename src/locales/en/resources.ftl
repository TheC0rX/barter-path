# --- ITEM CARD
item_card-selected_item =
    { $icon } Selected item: { $item_name }

item_card-selected_offer =
    { $icon } Selected offer: { $offer }

item_card-selected_discount =
    🎟️ Selected discount: { $discount }%

item_card-required_ings =
    📋 Required resources:

item_card-pieces =
    { $amount ->
        [one] pc.
       *[other] pcs.
    }

item_card-remains =
    └ { $amount } Remaining.

# --- ACTIVATING DISCOUNT
select-discount =
    🎯 Select the discount you want to apply.

discount-preview = 
    🎟️ Preview with { $discount }% discount applied.

activate_discount-activated =
    ✅ Discount { $discount }% was successfully applied to task { $item_name }.

# --- RESOURCE MANAGER
select-ingredient =
    🎯 Select the ingredient you want to edit.

type-resources =
    📝 Type the amount of resources to add them.

reset-description =
    🔄️ You can also reset the progress of collecting, by clicking reset button.

resource-already-finished =
    ⚠️ The resource was already collected.

must-be-number =
    ⚠️ Resource amount must be a number.

must-be-more-zero =
    ⚠️ Resource amount must be greater than 0.

must-be-less-limit =
    ⚠️ Resource amount must be less than 100 million.

adding_resources-confirmation =
    ❓ Are you sure you want to add { $amount } { $ing_name } for { $item_name }?

reset_resources-confirmation =
    ❓ Are you sure you want to reset the progress of { $ing_name } for { $item_name }?

update_resources-updated =
    ✅ Resources have been successfully updated.

# --- INGREDIENT CARD
ing_card-selected_item =
    { $icon } Selected resource: { $ing_name }

ing_card-ing_progress =
    { $icon } Collected { $collected_amount } of { $required_amount }

# --- INGREDIENT FORMAT
ing_format-main_menu =
    { $icon } { $item }: { $collected_amount }/{ $required_amount } { $unit }

ing_format-discount_menu =
    - { $item }: <s>{ $amount }</s> { $discount_amount } { $unit }

ing_format-resource_amount =
    - { $item }: { $amount } { $unit }