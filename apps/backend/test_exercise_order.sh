#!/bin/bash

# Script para probar el comportamiento del exercise_order

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU1NzA5NTIyLCJqdGkiOiJkYjVkNmQ4ZS00ZjE3LTQxOTUtOGVjMy0yYTA1NDVlY2U0NTUifQ.VP_p1VGpkfERMlQgCn4m9u9Ej06hRYLUeIjVDQpakhU"

echo "🧪 Probando comportamiento del exercise_order"

echo ""
echo "1️⃣ Crear ejercicio SIN especificar exercise_order (debería ir al final):"
curl -X POST "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "standard_exercise_id": 1,
    "block": "main",
    "sets": 3,
    "reps": 10,
    "load_type": "rpe",
    "rpe_target": 7.5
  }' | jq '.exercise_order'

echo ""
echo "2️⃣ Crear ejercicio CON exercise_order=1 (debería insertarse en posición 1):"
curl -X POST "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "standard_exercise_id": 2,
    "block": "main",
    "exercise_order": 1,
    "sets": 4,
    "reps": 8,
    "load_type": "rpe",
    "rpe_target": 8.0
  }' | jq '.exercise_order'

echo ""
echo "3️⃣ Listar ejercicios para verificar orden:"
curl -X GET "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises" \
  -H "Authorization: Bearer $TOKEN" | jq '.main[] | {id: .id, exercise_order: .exercise_order, exercise_name: .exercise_name}'

echo ""
echo "4️⃣ Probar reordenamiento:"
curl -X PATCH "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercises": [
      {"id": 5, "exercise_order": 1},
      {"id": 4, "exercise_order": 0}
    ]
  }' | jq '.[] | {id: .id, exercise_order: .exercise_order, exercise_name: .exercise_name}'

echo ""
echo "✅ Pruebas completadas"
