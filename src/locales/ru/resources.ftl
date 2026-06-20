# --- ITEM CARD
item_card-selected_item =
    <p><b>{ $icon } Выбранный предмет:</b> { $item_name }</p>

item_card-selected_offer =
    <p><b>{ $icon } Выбранное предложение:</b> { $offer }{ $total_offers }</p>

item_card-selected_discount =
    <p><b>🎟️ Выбранная скидка:</b> { $discount }%</p>

item_card-required_ings =
    <p><b>📋 Необходимые ресурсы:</b></p>

item_card-pieces = шт.

item_card-remains =
    <p>└ Осталось { $amount }.</p>

# --- ACTIVATING DISCOUNT
select-discount =
    <p>🎯 Выберите скидку, которую хотите применить.</p>

discount-preview = 
    <p>🎟️ Предварительный просмотр с учётом скидки <b><u>{ $discount }</u></b>%.</p>

# --- RESOURCE MANAGER
select-ingredient =
    <p>🎯 Выберите ресурс, который хотите редактировать.</p>

type-resources =
    <p>📝 Введите количество ресурсов для добавления.</p>

reset-description =
    <p>🔄️ Вы также можете сбросить прогресс сбора до нуля, нажав на кнопку сброса.</p>

resource-already-finished =
    <p>⚠️ Данный ресурс был уже собран.</p>

must-be-number =
    <p>⚠️ Количество ресурсов должно быть написано цифрами.</p>

must-be-more-zero =
    <p>⚠️ Количество ресурсов должно быть больше нуля.</p>

must-be-less-limit =
    <p>⚠️ Количество ресурсов должно быть меньше 100 миллионов.</p>

adding_resources-confirmation =
    <p>❓ Вы уверены, что хотите добавить <b>{ $amount }</b> <b>{ $ing_name }</b> для <b>{ $item_name }</b>?</p>

reset_resources-confirmation =
    <p>❓ Вы уверены, что хотите сбросить прогресс <b>{ $ing_name }</b> для <b>{ $item_name }</b>?</p>

# --- INGREDIENT CARD
ing_card-selected_item =
    <p><b>📦 Выбранный ресурс:</b> { $ing_name }</p>

ing_card-ing_progress =
    <p>{ $icon } Собранно { $collected_amount } из { $required_amount } { $unit }</p>

# --- INGREDIENT FORMAT
ing_format-main_menu =
    <p>{ $icon } { $item }: { $collected_amount }/{ $required_amount } { $unit }</p>

ing_format-discount_menu =
    <p>- { $item }: <s>{ $amount }</s> { $discount_amount } { $unit }</p>

ing_format-resource_amount =
    <p>- { $item }: { $amount } { $unit }</p>