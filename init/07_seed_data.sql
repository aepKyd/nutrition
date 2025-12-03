--
-- 07_seed_data.sql
--
-- Заполнение базы данных начальными данными
--

SET search_path = nutrition, public;

-- 1. Категории ингредиентов (10 записей)
INSERT INTO nutrition.ingredient_categories (name, description) VALUES
('Мясо', 'Различные виды мяса'),
('Птица', 'Различные виды птицы'),
('Рыба и морепродукты', 'Рыба, креветки, мидии и т.д.'),
('Молочные продукты', 'Молоко, сыр, творог, йогурт'),
('Яйца', 'Куриные, перепелиные яйца'),
('Крупы и злаки', 'Рис, гречка, овсянка, хлеб'),
('Овощи', 'Свежие, замороженные овощи'),
('Фрукты и ягоды', 'Свежие, замороженные фрукты и ягоды'),
('Бобовые', 'Горох, фасоль, чечевица'),
('Орехи и семена', 'Миндаль, фундук, семена чиа'),
('Масла и жиры', 'Растительные масла, сливочное масло'),
('Сладости и десерты', 'Сахар, мед, шоколад, выпечка'),
('Напитки', 'Соки, чай, кофе, вода');


-- 2. Категории рецептов (9 записей)
INSERT INTO nutrition.recipe_categories (name, description) VALUES
('Завтраки', 'Рецепты для утреннего приема пищи'),
('Основные блюда', 'Рецепты для обеда и ужина'),
('Супы', 'Первые блюда'),
('Салаты', 'Легкие закуски и гарниры'),
('Десерты', 'Сладкие блюда'),
('Выпечка', 'Хлебобулочные изделия и пироги'),
('Напитки', 'Рецепты различных напитков'),
('Закуски', 'Быстрые и легкие закуски'),
('Соусы', 'Дополнения к основным блюдам');


-- 3. Ингредиенты (50-70 записей)
INSERT INTO nutrition.ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs) VALUES
-- Мясо (id 1)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Мясо'), 'Говядина, филе', 'говядина филе', 158, 21.0, 7.0, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Мясо'), 'Свинина, нежирная', 'свинина нежирная', 160, 19.4, 9.5, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Мясо'), 'Баранина, лопатка', 'баранина лопатка', 203, 17.0, 15.0, 0.0),
-- Птица (id 2)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Птица'), 'Курица, грудка', 'курица грудка', 113, 23.6, 1.9, 0.4),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Птица'), 'Курица, бедро', 'курица бедро', 161, 18.2, 9.7, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Птица'), 'Индейка, филе', 'индейка филе', 115, 24.0, 2.0, 0.0),
-- Рыба и морепродукты (id 3)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Рыба и морепродукты'), 'Лосось', 'лосось', 208, 20.4, 13.4, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Рыба и морепродукты'), 'Треска', 'треска', 82, 17.8, 0.7, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Рыба и морепродукты'), 'Креветки', 'креветки', 85, 17.0, 1.7, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Рыба и морепродукты'), 'Тунец консервированный в собств. соку', 'тунец консервированный в собственном соку', 116, 25.5, 1.1, 0.0),
-- Молочные продукты (id 4)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Молочные продукты'), 'Молоко 3.2%', 'молоко 3 2', 59, 3.0, 3.2, 4.7),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Молочные продукты'), 'Кефир 2.5%', 'кефир 2 5', 53, 2.8, 2.5, 3.9),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Молочные продукты'), 'Творог 9%', 'творог 9', 169, 16.7, 9.0, 2.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Молочные продукты'), 'Сыр "Российский"', 'сыр российский', 363, 23.2, 29.5, 0.3),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Молочные продукты'), 'Йогурт натуральный 2%', 'йогурт натуральный 2', 60, 4.3, 2.0, 6.2),
-- Яйца (id 5)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Яйца'), 'Яйцо куриное', 'яйцо куриное', 155, 12.7, 10.9, 0.7),
-- Крупы и злаки (id 6)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Крупы и злаки'), 'Гречневая крупа (сухая)', 'гречневая крупа сухая', 343, 12.6, 3.3, 62.1),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Крупы и злаки'), 'Рис белый (сухой)', 'рис белый сухой', 360, 6.7, 0.7, 78.9),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Крупы и злаки'), 'Овсяные хлопья (сухие)', 'овсяные хлопья сухие', 389, 13.1, 6.9, 66.2),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Крупы и злаки'), 'Хлеб пшеничный', 'хлеб пшеничный', 265, 8.1, 3.2, 49.3),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Крупы и злаки'), 'Макароны (сухие)', 'макароны сухие', 342, 11.0, 1.5, 70.0),
-- Овощи (id 7)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Огурец', 'огурец', 15, 0.7, 0.1, 3.6),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Помидор', 'помидор', 18, 0.9, 0.2, 3.9),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Картофель', 'картофель', 77, 2.0, 0.1, 17.5),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Морковь', 'морковь', 41, 0.9, 0.2, 9.6),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Капуста белокочанная', 'капуста белокочанная', 25, 1.3, 0.1, 5.8),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Лук репчатый', 'лук репчатый', 40, 1.1, 0.1, 9.3),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Овощи'), 'Перец болгарский', 'перец болгарский', 20, 1.0, 0.3, 4.6),
-- Фрукты и ягоды (id 8)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Фрукты и ягоды'), 'Яблоко', 'яблоко', 52, 0.3, 0.2, 13.8),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Фрукты и ягоды'), 'Банан', 'банан', 89, 1.1, 0.3, 22.8),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Фрукты и ягоды'), 'Апельсин', 'апельсин', 47, 0.9, 0.1, 11.8),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Фрукты и ягоды'), 'Клубника', 'клубника', 32, 0.7, 0.3, 7.7),
-- Бобовые (id 9)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Бобовые'), 'Чечевица (сухая)', 'чечевица сухая', 352, 24.6, 1.1, 63.4),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Бобовые'), 'Фасоль красная (сухая)', 'фасоль красная сухая', 337, 22.5, 0.5, 61.2),
-- Орехи и семена (id 10)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Орехи и семена'), 'Миндаль', 'миндаль', 579, 21.2, 49.9, 21.6),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Орехи и семена'), 'Грецкий орех', 'грецкий орех', 654, 15.2, 65.2, 13.7),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Орехи и семена'), 'Семена чиа', 'семена чиа', 486, 17.0, 30.7, 42.1),
-- Масла и жиры (id 11)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Масла и жиры'), 'Масло подсолнечное', 'масло подсолнечное', 899, 0.0, 99.9, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Масла и жиры'), 'Масло оливковое', 'масло оливковое', 884, 0.0, 99.9, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Масла и жиры'), 'Масло сливочное 82.5%', 'масло сливочное 82 5', 748, 0.5, 82.5, 0.8),
-- Сладости и десерты (id 12)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Сладости и десерты'), 'Сахар', 'сахар', 387, 0.0, 0.0, 100.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Сладости и десерты'), 'Мед', 'мед', 304, 0.3, 0.0, 82.4),
-- Напитки (id 13)
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Напитки'), 'Вода питьевая', 'вода питьевая', 0, 0.0, 0.0, 0.0),
((SELECT id FROM nutrition.ingredient_categories WHERE name = 'Напитки'), 'Чай черный', 'чай черный', 1, 0.1, 0.0, 0.3);


-- 4. Синонимы (20-30 записей)
INSERT INTO nutrition.ingredient_synonyms (ingredient_id, synonym, synonym_normalized) VALUES
((SELECT id FROM nutrition.ingredients WHERE name = 'Курица, грудка'), 'Куриное филе', 'куриное филе'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Курица, грудка'), 'Филе куриное', 'филе куриное'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Говядина, филе'), 'Филе говядины', 'филе говядины'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Индейка, филе'), 'Филе индейки', 'филе индейки'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Яйцо куриное'), 'Яйца', 'яйца'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Яйцо куриное'), 'Яичко', 'яичко'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Гречневая крупа (сухая)'), 'Гречка', 'гречка'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Рис белый (сухой)'), 'Рис', 'рис'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Овсяные хлопья (сухие)'), 'Овсянка', 'овсянка'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Макароны (сухие)'), 'Паста', 'паста'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Огурец'), 'Огурчик', 'огурчик'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Помидор'), 'Томат', 'томат'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Картофель'), 'Картошка', 'картошка'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Морковь'), 'Морковка', 'морковка'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Капуста белокочанная'), 'Капуста', 'капуста'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Лук репчатый'), 'Лук', 'лук'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Перец болгарский'), 'Сладкий перец', 'сладкий перец'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Яблоко'), 'Яблоки', 'яблоки'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Банан'), 'Бананы', 'бананы'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Апельсин'), 'Апельсины', 'апельсины'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Клубника'), 'Земляника садовая', 'земляника садовая'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Чечевица (сухая)'), 'Лентиль', 'лентиль'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Фасоль красная (сухая)'), 'Фасоль', 'фасоль'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Масло подсолнечное'), 'Подсолнечное масло', 'подсолнечное масло'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Масло оливковое'), 'Оливковое масло', 'оливковое масло'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Сахар'), 'Сахарок', 'сахарок'),
((SELECT id FROM nutrition.ingredients WHERE name = 'Мед'), 'Медок', 'медок');


-- 5. Рецепты (3-5 записей)
INSERT INTO nutrition.recipes (category_id, name, description, instructions) VALUES
    ((SELECT id FROM nutrition.recipe_categories WHERE name = 'Основные блюда'), 'Гречка с курицей', 'Простое и питательное блюдо', '1. Отварить гречку. 2. Отварить куриную грудку. 3. Подавать вместе.'),
    ((SELECT id FROM nutrition.recipe_categories WHERE name = 'Завтраки'), 'Овсянка на молоке', 'Быстрый и полезный завтрак', '1. Смешать овсянку с молоком и щепоткой соли. 2. Довести до кипения и варить 5 минут. 3. Подавать с фруктами или медом.'),
    ((SELECT id FROM nutrition.recipe_categories WHERE name = 'Завтраки'), 'Омлет', 'Классический омлет на завтрак', '1. Взбить яйца с молоком. 2. Разогреть масло на сковороде. 3. Вылить яичную смесь и жарить до готовности.');

-- 6. Ингредиенты рецептов
INSERT INTO nutrition.recipe_ingredients (recipe_id, ingredient_id, weight_grams) VALUES
    -- Гречка с курицей
    ((SELECT id FROM nutrition.recipes WHERE name = 'Гречка с курицей'), (SELECT id FROM nutrition.ingredients WHERE name = 'Гречневая крупа (сухая)'), 100),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Гречка с курицей'), (SELECT id FROM nutrition.ingredients WHERE name = 'Курица, грудка'), 150),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Гречка с курицей'), (SELECT id FROM nutrition.ingredients WHERE name = 'Масло подсолнечное'), 5),
    -- Овсянка на молоке
    ((SELECT id FROM nutrition.recipes WHERE name = 'Овсянка на молоке'), (SELECT id FROM nutrition.ingredients WHERE name = 'Овсяные хлопья (сухие)'), 50),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Овсянка на молоке'), (SELECT id FROM nutrition.ingredients WHERE name = 'Молоко 3.2%'), 200),
    -- Омлет
    ((SELECT id FROM nutrition.recipes WHERE name = 'Омлет'), (SELECT id FROM nutrition.ingredients WHERE name = 'Яйцо куриное'), 120), -- ~2 яйца
    ((SELECT id FROM nutrition.recipes WHERE name = 'Омлет'), (SELECT id FROM nutrition.ingredients WHERE name = 'Молоко 3.2%'), 50),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Омлет'), (SELECT id FROM nutrition.ingredients WHERE name = 'Масло сливочное 82.5%'), 5);