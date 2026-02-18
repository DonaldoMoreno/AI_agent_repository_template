# TEMPLATE PROMPT

## Context
Estamos construyendo DummyLux con C++20, CMake, vcpkg. No cambiar stack.

## Task
Implementar Issue X exactamente.

## Constraints

- No refactors masivos
- No dependencias nuevas salvo aprobación (y justificar)
- Mantener CI verde (windows + ubuntu)

## Deliverables
Lista exacta de archivos a crear/modificar

## Acceptance Criteria
Lista medible

## Commands

```bash
cmake -S . -B build -G Ninja
cmake --build build --config Release
```

## Out of scope
Cosas que NO debe tocar
