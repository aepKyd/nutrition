--
-- 04_create_triggers.sql
--
-- Создание функций и триггеров для автоматизации и нормализации данных
--

SET search_path = nutrition, public;

-- a) normalize_ingredient_name() + триггер
-- Нормализует имя ингредиента (удаляет пробелы, переводит в нижний регистр, заменяет 'ё' на 'е')
CREATE OR REPLACE FUNCTION nutrition.normalize_ingredient_name()
RETURNS TRIGGER AS $$
BEGIN
  NEW.name_normalized := TRIM(
    REGEXP_REPLACE(
      REPLACE(LOWER(NEW.name), 'ё', 'е'),
      '\s+', ' ', 'g'
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_normalize_ingredient_name
BEFORE INSERT OR UPDATE ON nutrition.ingredients
FOR EACH ROW EXECUTE FUNCTION nutrition.normalize_ingredient_name();

-- b) normalize_synonym() + триггер (аналогично для синонимов)
-- Нормализует синоним ингредиента
CREATE OR REPLACE FUNCTION nutrition.normalize_synonym()
RETURNS TRIGGER AS $$
BEGIN
  NEW.synonym_normalized := TRIM(
    REGEXP_REPLACE(
      REPLACE(LOWER(NEW.synonym), 'ё', 'е'),
      '\s+', ' ', 'g'
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_normalize_synonym
BEFORE INSERT OR UPDATE ON nutrition.ingredient_synonyms
FOR EACH ROW EXECUTE FUNCTION nutrition.normalize_synonym();


-- c) recalculate_dish_nutrition() + триггер
-- Пересчитывает КБЖУ приготовленного блюда при изменении его ингредиентов
CREATE OR REPLACE FUNCTION nutrition.recalculate_dish_nutrition()
RETURNS TRIGGER AS $$
DECLARE
  v_total_calories NUMERIC(10, 2) := 0;
  v_total_proteins NUMERIC(10, 2) := 0;
  v_total_fats     NUMERIC(10, 2) := 0;
  v_total_carbs    NUMERIC(10, 2) := 0;
  v_initial_weight NUMERIC(10, 2) := 0;
  v_cooked_dish_id BIGINT;
BEGIN
  IF TG_OP = 'DELETE' THEN
    v_cooked_dish_id := OLD.cooked_dish_id;
  ELSE -- INSERT or UPDATE
    v_cooked_dish_id := NEW.cooked_dish_id;
  END IF;

  -- Суммируем КБЖУ всех ингредиентов в блюде
  SELECT
    SUM(cdi.calories / 100 * cdi.weight_grams),
    SUM(cdi.proteins / 100 * cdi.weight_grams),
    SUM(cdi.fats / 100 * cdi.weight_grams),
    SUM(cdi.carbs / 100 * cdi.weight_grams),
    SUM(cdi.weight_grams)
  INTO
    v_total_calories, v_total_proteins, v_total_fats, v_total_carbs, v_initial_weight
  FROM nutrition.cooked_dish_ingredients cdi
  WHERE cdi.cooked_dish_id = v_cooked_dish_id;

  -- Обновляем cooked_dishes
  UPDATE nutrition.cooked_dishes
  SET
    initial_weight = COALESCE(v_initial_weight, 0),
    total_calories = COALESCE(v_total_calories, 0),
    total_proteins = COALESCE(v_total_proteins, 0),
    total_fats     = COALESCE(v_total_fats, 0),
    total_carbs    = COALESCE(v_total_carbs, 0)
  WHERE id = v_cooked_dish_id;

  RETURN NULL; -- AFTER триггер не должен возвращать строку
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_recalculate_dish_nutrition
AFTER INSERT OR UPDATE OR DELETE ON nutrition.cooked_dish_ingredients
FOR EACH ROW EXECUTE FUNCTION nutrition.recalculate_dish_nutrition();


-- d) calculate_consumed_nutrition() + триггер
-- Рассчитывает КБЖУ потребленной порции и проверяет остаток блюда
CREATE OR REPLACE FUNCTION nutrition.calculate_consumed_nutrition()
RETURNS TRIGGER AS $$
DECLARE
  v_dish_calories NUMERIC(10, 2);
  v_dish_proteins NUMERIC(10, 2);
  v_dish_fats     NUMERIC(10, 2);
  v_dish_carbs    NUMERIC(10, 2);
  v_dish_final_weight NUMERIC(10, 2);
  v_dish_remaining_weight NUMERIC(10, 2);
  v_portion_coefficient NUMERIC(10, 4);
BEGIN
  -- Получаем КБЖУ и вес блюда
  SELECT
    cd.total_calories,
    cd.total_proteins,
    cd.total_fats,
    cd.total_carbs,
    cd.final_weight,
    cd.remaining_weight
  INTO
    v_dish_calories,
    v_dish_proteins,
    v_dish_fats,
    v_dish_carbs,
    v_dish_final_weight,
    v_dish_remaining_weight
  FROM nutrition.cooked_dishes cd
  WHERE cd.id = NEW.cooked_dish_id
  FOR UPDATE; -- Блокируем строку, чтобы избежать гонок при параллельном потреблении

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Приготовленное блюдо с ID % не найдено.', NEW.cooked_dish_id;
  END IF;

  -- Проверяем, достаточно ли осталось блюда
  IF NEW.weight_grams > v_dish_remaining_weight THEN
    -- Если хотим съесть больше, чем есть, то урезаем порцию до остатка
    NEW.weight_grams := v_dish_remaining_weight;
    RAISE WARNING 'Порция была урезана до оставшегося веса блюда (%).', v_dish_remaining_weight;
  END IF;

  -- Если блюда не осталось, не позволяем потреблять
  IF NEW.weight_grams <= 0 THEN
      RAISE EXCEPTION 'Нечего потреблять, оставшийся вес блюда равен 0.';
  END IF;


  -- Рассчитываем КБЖУ порции
  v_portion_coefficient := NEW.weight_grams / v_dish_final_weight;

  NEW.calories := v_dish_calories * v_portion_coefficient;
  NEW.proteins := v_dish_proteins * v_portion_coefficient;
  NEW.fats     := v_dish_fats * v_portion_coefficient;
  NEW.carbs    := v_dish_carbs * v_portion_coefficient;

  -- Обновляем оставшийся вес блюда
  IF TG_OP = 'INSERT' THEN
      UPDATE nutrition.cooked_dishes
      SET remaining_weight = remaining_weight - NEW.weight_grams
      WHERE id = NEW.cooked_dish_id;
  ELSIF TG_OP = 'UPDATE' THEN
      -- Для UPDATE сначала восстанавливаем старый вес, потом вычитаем новый
      -- Но мы не можем менять remaining_weight здесь так просто, потому что мы внутри BEFORE UPDATE
      -- Проще сделать это в AFTER UPDATE или здесь, но с учетом разницы.
      -- НО! calculate_consumed_nutrition вызывается BEFORE, чтобы рассчитать макросы.
      -- Логика remaining_weight должна быть консистентной.
      -- Сделаем так:
      -- 1. Считаем дельту веса (NEW.weight_grams - OLD.weight_grams)
      -- 2. Если дельта > 0, проверяем хватает ли.
      -- 3. Обновляем remaining_weight.
      
      -- Однако, v_dish_remaining_weight получен выше из базы. Это ТЕКУЩИЙ остаток.
      -- Если мы обновляем запись, то "текущий остаток" уже учитывает то, что мы "съели" в OLD.weight_grams? Нет.
      -- cooked_dishes.remaining_weight хранится отдельно.
      -- Пример: Блюдо 1000г. Съели 200г. Остаток 800г.
      -- UPDATE: меняем 200г на 300г.
      -- Нам нужно уменьшить остаток еще на 100г. Итого 700г.
      -- Дельта = 300 - 200 = 100.
      -- Если дельта > 800 (остаток), то ошибка/ворнинг.
      
      -- Нюанс: v_dish_remaining_weight из SELECT ... INTO ... это остаток В БАЗЕ (800г).
      -- Нам нужно проверить (NEW.weight_grams - OLD.weight_grams) > v_dish_remaining_weight.
      
      DECLARE
        v_weight_delta NUMERIC(10, 2);
      BEGIN
        v_weight_delta := NEW.weight_grams - OLD.weight_grams;
        
        IF v_weight_delta > v_dish_remaining_weight THEN
            -- Не хватает остатка, чтобы увеличить порцию
             NEW.weight_grams := OLD.weight_grams + v_dish_remaining_weight;
             v_weight_delta := v_dish_remaining_weight; -- забираем всё что есть
             RAISE WARNING 'Порция была урезана до максимально доступного (%).', NEW.weight_grams;
        END IF;

        UPDATE nutrition.cooked_dishes
        SET remaining_weight = remaining_weight - v_weight_delta
        WHERE id = NEW.cooked_dish_id;
        
        -- Пересчет макросов для новой порции (так же как в INSERT)
         v_portion_coefficient := NEW.weight_grams / v_dish_final_weight;
         NEW.calories := v_dish_calories * v_portion_coefficient;
         NEW.proteins := v_dish_proteins * v_portion_coefficient;
         NEW.fats     := v_dish_fats * v_portion_coefficient;
         NEW.carbs    := v_dish_carbs * v_portion_coefficient;
      END;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_consumed_nutrition
BEFORE INSERT OR UPDATE ON nutrition.consumed
FOR EACH ROW EXECUTE FUNCTION nutrition.calculate_consumed_nutrition();

-- g) restore_dish_weight_on_delete() + триггер
-- Восстанавливает вес блюда при удалении записи о потреблении
CREATE OR REPLACE FUNCTION nutrition.restore_dish_weight_on_delete()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE nutrition.cooked_dishes
  SET remaining_weight = remaining_weight + OLD.weight_grams
  WHERE id = OLD.cooked_dish_id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_restore_dish_weight_on_delete
AFTER DELETE ON nutrition.consumed
FOR EACH ROW EXECUTE FUNCTION nutrition.restore_dish_weight_on_delete();


-- e) update_recipe_stats() + триггер
-- Обновляет статистику рецепта (times_cooked, avg_cooked_weight)
CREATE OR REPLACE FUNCTION nutrition.update_recipe_stats()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE nutrition.recipes
  SET
    times_cooked = times_cooked + 1,
    avg_cooked_weight = (
      SELECT AVG(final_weight)
      FROM nutrition.cooked_dishes
      WHERE recipe_id = NEW.recipe_id
    )
  WHERE id = NEW.recipe_id;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_recipe_stats
AFTER INSERT ON nutrition.cooked_dishes
FOR EACH ROW EXECUTE FUNCTION nutrition.update_recipe_stats();


-- f) update_updated_at() + триггер
-- Обновляет колонку updated_at для таблицы recipes
CREATE OR REPLACE FUNCTION nutrition.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_recipe_updated_at
BEFORE UPDATE ON nutrition.recipes
FOR EACH ROW EXECUTE FUNCTION nutrition.update_updated_at();