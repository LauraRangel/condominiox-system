# Guion de diapositivas (5 slides)

## 1. Titulo
- CondominioX: Uso de estructuras de datos
- Curso: Algoritmos y Estructuras de Datos
- Autora: Laura Rangel

## 2. Contexto del proyecto
- Sistema web para gestion de condominios
- Modulos: propietarios, gastos, recibos
- Backend en Flask + PostgreSQL

## 3. Lista enlazada de propietarios
- Estructura: nodos con data + next
- Operaciones: insertar, eliminar, recorrer
- Uso real: GET /api/propietarios (backend)

## 4. Matriz de recibos por mes
- Estructura: meses[mes][propietario_id] = recibo
- Permite agrupar y resumir por mes
- Uso real: GET /api/recibos y filtros por mes

## 5. Impacto en el sistema
- Organizacion y rendimiento (O(1) en acceso por clave)
- Resumen mensual: emitido, pagado, pendiente
- Visualizacion en panel admin + lista detallada
