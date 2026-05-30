# --- ITEM CARD
item_card-selected_item =
    { $icon } Выбранный предмет: { $item_name }

item_card-selected_offer =
    { $icon } Выбранное предложение: { $offer }

item_card-selected_discount =
    🎟️ Выбранная скидка: { $discount }%

item_card-required_ings =
    📋 Необходимые ресурсы:

item_card-pieces =
    шт.

item_card-remains =
    └ Осталось { $amount }.

# --- ACTIVATING DISCOUNT
select-discount =
    🎯 Выберите скидку, которую хотите применить.

discount-preview = 
    🎟️ Предварительный просмотр с учётом скидки { $discount }%.

activate_discount-activated =
    ✅ Скидка { $discount } была успешно применена к задаче на { $item_name }.

# --- RESOURCE MANAGER
select-ingredient =
    🎯 Выберите ресурс, который хотите редактировать.

type-resources =
    📝 Введите количество ресурсов для добавления.

reset-description =
    🔄️ Вы также можете сбросить прогресс сбора до нуля, нажав на кнопку сброса.

resource-already-finished =
    ⚠️ Данный ресурс был уже собран.

must-be-number =
    ⚠️ Количество ресурсов должно быть написано цифрами.

must-be-more-zero =
    ⚠️ Количество ресурсов должно быть больше нуля.

additing_resources-confirmation =
    ❓ Вы уверены, что хотите добавить { $amount } { $ing_name } для { $item_name }?

reset_resources-confirmation =
    ❓ Вы уверены, что хотите сбросить прогресс { $ing_name } для { $item_name }?

update_resources-updated =
    ✅ Ресурсы были успешно обновлены.

# --- INGREDIENT CARD
ing_card-selected_item =
    { $icon } Выбранный ресурс: { $ing_name }

ing_card-ing_progress =
    { $icon } Собранно { $collected_amount } из { $required_amount }