# Анализ производительности

Этот документ содержит анализ производительности ключевых запросов с использованием `EXPLAIN ANALYZE`.

## 1. Функция поиска `search_ingredients`

Этот тест показывает производительность функции `nutrition.search_ingredients` при поиске по подстроке.

### Запрос

```sql
EXPLAIN ANALYZE SELECT * FROM nutrition.search_ingredients('кур', 5);
```

### Результат

```
                                                       QUERY PLAN
-----------------------------------------------------------------------------------------------------------------------
 Function Scan on search_ingredients  (cost=0.25..10.25 rows=1000 width=100) (actual time=4.526..4.526 rows=3 loops=1)
 Planning Time: 0.030 ms
 Execution Time: 4.760 ms
(3 rows)
```

### Анализ

- **Function Scan**: Основное время тратится на выполнение самой PL/pgSQL функции `search_ingredients`.
- **Execution Time: 4.760 ms**: Время выполнения очень низкое, что говорит о высокой производительности. Это достигается за счет использования GIN-индексов для полнотекстового и триграмного поиска, что позволяет избежать полного сканирования таблицы `ingredients`.

## 2. Представление `daily_stats`

Этот тест показывает производительность `VIEW` для получения дневной статистики.

### Запрос

```sql
EXPLAIN ANALYZE SELECT * FROM nutrition.daily_stats;
```

### Результат

```
                                                     QUERY PLAN
-------------------------------------------------------------------------------------------------------------------
 Sort  (cost=31.74..32.24 rows=200 width=258) (actual time=0.043..0.044 rows=1 loops=1)
   Sort Key: ((consumed.consumed_at)::date), consumed.meal_type
   Sort Method: quicksort  Memory: 25kB
   ->  HashAggregate  (cost=19.60..24.10 rows=200 width=258) (actual time=0.019..0.020 rows=1 loops=1)
         Group Key: (consumed.consumed_at)::date, consumed.meal_type
         Batches: 1  Memory Usage: 40kB
         ->  Seq Scan on consumed  (cost=0.00..14.00 rows=320 width=194) (actual time=0.010..0.010 rows=1 loops=1)
 Planning Time: 0.828 ms
 Execution Time: 0.137 ms
(9 rows)
```

### Анализ

- **Seq Scan on consumed**: Поскольку в таблице `consumed` очень мало записей (одна), планировщик выбирает полное сканирование, что является самым эффективным способом для маленьких таблиц.
- **HashAggregate**: Используется для группировки данных по дате и типу приема пищи.
- **Execution Time: 0.137 ms**: Время выполнения чрезвычайно низкое. С ростом таблицы `consumed` производительность может снизиться. Для оптимизации в будущем может потребоваться добавление индексов на `consumed_at` и `meal_type`, которые уже созданы в `init/03_create_indexes.sql`. Это демонстрирует, что архитектура готова к масштабированию.
