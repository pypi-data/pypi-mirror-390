# ETL Toolbox - Registry Guide

Tento dokument popisuje, jak explorovat dostupné služby, resources a operace v registru a jak spouštět volání přes registry.

## Obsah

1. [Inicializace Registry](#inicializace-registry)
2. [Explorace dostupných služeb](#explorace-dostupných-služeb)
3. [Explorace resources](#explorace-resources)
4. [Explorace operací](#explorace-operací)
5. [Získání detailů a parametrů](#získání-detailů-a-parametrů)
6. [Spuštění volání přes registry](#spuštění-volání-přes-registry)

## Inicializace Registry

Registry se automaticky inicializuje s auto-discovery a auto-generací manifestů:

```python
from connector.core.registry.service_registry import ServiceRegistry

# Vytvoření registry s automatickým objevováním služeb
registry = ServiceRegistry(
    auto_generate_manifests=True,  # Automaticky generuje manifesty
    auto_discover_openapi=True     # Automaticky objevuje OpenAPI schémata
)
```

Registry automaticky:
- Objevuje všechny služby v `src/connector/services/`
- Registruje OpenAPI služby ze schémat v `schemas/`
- Generuje manifesty pro metadata o parametrech

## Explorace dostupných služeb

### Seznam všech služeb

```python
# Získání seznamu všech registrovaných služeb
services = registry.list_services()
print(services)
# ['asana', 'clickup', 'fakturoid', 'google_sheets', ...]
```

### Vyhledávání služeb

```python
# Vyhledání služeb podle názvu (case-insensitive partial match)
results = registry.search_services(name_filter="google")
for service in results:
    print(f"Service: {service['name']}")
    print(f"Resources: {service['resources']}")
    print(f"Metadata: {service['metadata']}")
```

### Metadata služby

```python
# Získání kompletních metadat služby
metadata = registry.get_service_metadata("asana")
print(f"Base URL: {metadata['base_url']}")
print(f"Auth methods: {metadata['authentication_methods']}")
print(f"Resources: {metadata['resources']}")
print(f"Version: {metadata['version']}")
print(f"Description: {metadata['description']}")
```

### Manifest služby

```python
# Získání manifestu služby (obsahuje metadata o resources a operacích)
service_manifest = registry.get_service_manifest("asana")
print(f"Name: {service_manifest.name}")
print(f"Description: {service_manifest.description}")
print(f"Base URL: {service_manifest.base_url}")
print(f"Resources: {[r.name for r in service_manifest.resources]}")
```

## Explorace resources

### Seznam resources pro službu

```python
# Získání seznamu resources pro konkrétní službu
resources = registry.list_resources("asana")
print(resources)
# ['tasks', 'projects', 'workspaces', 'users', ...]
```

### Manifest resource

```python
# Získání manifestu resource (obsahuje metadata o operacích a parametrech)
resource_manifest = registry.get_resource_manifest("asana", "tasks")
print(f"Name: {resource_manifest.name}")
print(f"Description: {resource_manifest.description}")
print(f"Endpoint: {resource_manifest.endpoint}")
print(f"Operations: {[op.name for op in resource_manifest.operations]}")
```

## Explorace operací

### Seznam operací

```python
# Seznam všech operací pro službu
operations = registry.list_operations("asana")
print(operations)
# ['get_task', 'list_tasks', 'create_task', 'update_task', ...]

# Seznam operací pro konkrétní resource
operations = registry.list_operations("asana", "tasks")
print(operations)
# ['get_task', 'list_tasks', 'create_task', 'update_task', ...]
```

### Vyhledávání operací

```python
# Vyhledání operací s filtrováním
results = registry.search_operations(
    service_name="asana",
    resource_name="tasks",
    name_filter="get"  # Case-insensitive partial match
)

for op in results:
    print(f"Operation ID: {op['operation_id']}")
    print(f"Service: {op['service_name']}")
    print(f"Resource: {op['resource_name']}")
    print(f"Endpoint: {op['endpoint']}")
```

### Informace o operaci

```python
# Získání základních informací o operaci
operation_info = registry.get_operation_info("get_task", service_name="asana")
if operation_info:
    print(f"Service: {operation_info['service_name']}")
    print(f"Resource: {operation_info['resource_name']}")
    print(f"Endpoint: {operation_info['endpoint']}")
```

## Získání detailů a parametrů

### Kompletní detaily operace

```python
# Získání kompletních detailů operace včetně parametrů
details = registry.get_operation_details("get_task", service_name="asana")

if details:
    print(f"Operation ID: {details['operation_id']}")
    print(f"Service: {details['service_name']}")
    print(f"Resource: {details['resource_name']}")
    print(f"Endpoint: {details['endpoint']}")
    
    # Manifest obsahuje detailní informace o parametrech
    if details.get('manifest'):
        manifest = details['manifest']
        print(f"Name: {manifest.get('name')}")
        print(f"Description: {manifest.get('description')}")
        
        # Všechny parametry
        print("\nAll Parameters:")
        for param in manifest.get('parameters', []):
            print(f"  - {param['name']}: {param['type']} (required: {param['required']})")
            if param.get('description'):
                print(f"    Description: {param['description']}")
            if param.get('default') is not None:
                print(f"    Default: {param['default']}")
        
        # Pouze povinné parametry
        print("\nRequired Parameters:")
        for param in manifest.get('required_parameters', []):
            print(f"  - {param['name']}: {param['type']}")
            if param.get('description'):
                print(f"    Description: {param['description']}")
        
        # Pouze volitelné parametry
        print("\nOptional Parameters:")
        for param in manifest.get('optional_parameters', []):
            print(f"  - {param['name']}: {param['type']}")
            if param.get('default') is not None:
                print(f"    Default: {param['default']}")
        
        # Request/Response schémata (pro OpenAPI služby)
        if manifest.get('request_schema'):
            print(f"\nRequest Schema: {manifest['request_schema']}")
        if manifest.get('response_schema'):
            print(f"Response Schema: {manifest['response_schema']}")
        
        # Parametry s umístěním (pro OpenAPI služby)
        if manifest.get('parameters_with_location'):
            print("\nParameters with Location:")
            for param in manifest['parameters_with_location']:
                print(f"  - {param['name']}: {param['type']} in {param.get('in', 'body')}")
```

### Manifest operace

```python
# Získání manifestu operace přímo
operation_manifest = registry.get_operation_manifest(
    service_name="asana",
    resource_name="tasks",
    operation_name="get_task"
)

if operation_manifest:
    print(f"Name: {operation_manifest.name}")
    print(f"Description: {operation_manifest.description}")
    
    # Povinné parametry
    required_params = operation_manifest.get_required_parameters()
    print("\nRequired Parameters:")
    for param in required_params:
        print(f"  - {param.name}: {param.type}")
        if param.description:
            print(f"    {param.description}")
    
    # Všechny parametry
    print("\nAll Parameters:")
    for param in operation_manifest.parameters:
        print(f"  - {param.name}: {param.type} (required: {param.required})")
        if param.default is not None:
            print(f"    Default: {param.default}")
```

## Spuštění volání přes registry

### Použití RunConfiguration

`RunConfiguration` je doporučený způsob pro spouštění operací přes registry:

```python
from connector.core.run_configuration import RunConfiguration

# Vytvoření RunConfiguration s registry
run_config = RunConfiguration(registry)

# Konfigurace pro spuštění operace
config = {
    "service": "asana",
    "resource": "tasks",
    "operation_id": "get_task",  # Volitelné, pokud je v parameters
    "service_config": {
        # Konfigurace služby (např. auth credentials)
        "base_url": "https://app.asana.com/api/1.0",
        # ... další service config
    },
    "resource_config": {
        # Konfigurace resource (např. endpoint)
        "endpoint": "/tasks",
        # ... další resource config
    },
    "parameters": {
        "operation_id": "get_task",  # Pokud není v root config
        "task_gid": "123456789",
        "opt_fields": ["name", "notes", "assignee"]
    }
}

# Spuštění operace
result = run_config.execute_run(config)
print(result)
```

### Auto-detekce resource z operation_id

Pokud znáte `operation_id` a `service`, můžete nechat registry automaticky detekovat resource:

```python
config = {
    "service": "asana",
    # resource není potřeba - bude auto-detekován z operation_id
    "operation_id": "get_task",
    "parameters": {
        "task_gid": "123456789"
    }
}

result = run_config.execute_run(config)
```

### Přímé použití registry

Můžete také vytvořit instance přímo z registry:

```python
# Získání tříd ze registry
service_class = registry.get_service("asana")
resource_class = registry.get_resource("asana", "tasks")

# Vytvoření instancí
service_instance = service_class(
    base_url="https://app.asana.com/api/1.0",
    # ... další config
)

resource_instance = resource_class(
    service=service_instance,
    endpoint="/tasks"
)

# Spuštění operace
result = resource_instance.run({
    "operation_id": "get_task",
    "task_gid": "123456789"
})
```

## Příklady použití

### Kompletní workflow: Explorace → Získání parametrů → Spuštění

```python
from connector.core.registry.service_registry import ServiceRegistry
from connector.core.run_configuration import RunConfiguration

# 1. Inicializace
registry = ServiceRegistry(auto_generate_manifests=True)
run_config = RunConfiguration(registry)

# 2. Explorace - najít všechny služby obsahující "google"
services = registry.search_services(name_filter="google")
print("Found services:", [s['name'] for s in services])

# 3. Explorace - najít všechny resources pro službu
resources = registry.list_resources("google_sheets")
print("Available resources:", resources)

# 4. Explorace - najít všechny operace pro resource
operations = registry.list_operations("google_sheets", "spreadsheet")
print("Available operations:", operations)

# 5. Získání detailů operace včetně parametrů
details = registry.get_operation_details("read_spreadsheet", service_name="google_sheets")
if details and details.get('manifest'):
    manifest = details['manifest']
    print("\nOperation Parameters:")
    for param in manifest.get('required_parameters', []):
        print(f"  Required: {param['name']} ({param['type']})")
    for param in manifest.get('optional_parameters', []):
        print(f"  Optional: {param['name']} ({param['type']})")

# 6. Spuštění operace
config = {
    "service": "google_sheets",
    "resource": "spreadsheet",
    "parameters": {
        "operation_id": "read_spreadsheet",
        "spreadsheet_id": "your-spreadsheet-id",
        "range": "A1:B10"
    }
}

result = run_config.execute_run(config)
print("\nResult:", result)
```

### Interaktivní explorace

```python
def explore_service(registry, service_name):
    """Interaktivní explorace služby"""
    print(f"\n=== Exploring Service: {service_name} ===")
    
    # Metadata služby
    metadata = registry.get_service_metadata(service_name)
    print(f"\nBase URL: {metadata.get('base_url')}")
    print(f"Description: {metadata.get('description')}")
    print(f"Auth Methods: {metadata.get('authentication_methods')}")
    
    # Resources
    resources = registry.list_resources(service_name)
    print(f"\nResources ({len(resources)}):")
    for resource_name in resources:
        print(f"  - {resource_name}")
        
        # Operace pro každý resource
        operations = registry.list_operations(service_name, resource_name)
        print(f"    Operations ({len(operations)}):")
        for op_id in operations[:5]:  # Zobrazit prvních 5
            print(f"      - {op_id}")
        if len(operations) > 5:
            print(f"      ... and {len(operations) - 5} more")

# Použití
registry = ServiceRegistry(auto_generate_manifests=True)
explore_service(registry, "asana")
explore_service(registry, "fakturoid")
```

## Tipy a triky

### 1. Validace konfigurace před spuštěním

```python
# Validace konfigurace bez spuštění
try:
    run_config.validate_config(config)
    print("Configuration is valid!")
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### 2. Získání dostupných services/resources

```python
# Seznam všech dostupných služeb
services = run_config.get_available_services()
print("Available services:", services)

# Seznam resources pro službu
resources = run_config.get_available_resources("asana")
print("Available resources for asana:", resources)
```

### 3. Hledání operací podle klíčového slova

```python
# Najít všechny operace obsahující "list"
results = registry.search_operations(name_filter="list")
for op in results:
    print(f"{op['service_name']}.{op['resource_name']}.{op['operation_id']}")
```

### 4. Získání OpenAPI schémat pro operace

Pro OpenAPI služby můžete získat detailní informace o request/response schématech:

```python
details = registry.get_operation_details("get_task", service_name="asana")
if details and details.get('manifest'):
    manifest = details['manifest']
    
    # Request schema (pro POST/PUT operace)
    if manifest.get('request_schema'):
        print("Request Schema:", manifest['request_schema'])
    
    # Response schema
    if manifest.get('response_schema'):
        print("Response Schema:", manifest['response_schema'])
    
    # HTTP metoda a path
    if manifest.get('method'):
        print(f"Method: {manifest['method']}")
    if manifest.get('path'):
        print(f"Path: {manifest['path']}")
```

## Shrnutí

- **Explorace**: Použijte `list_services()`, `list_resources()`, `list_operations()` a `search_*()` metody
- **Parametry**: Použijte `get_operation_details()` nebo `get_operation_manifest()` pro získání informací o parametrech
- **Spuštění**: Použijte `RunConfiguration.execute_run()` pro spuštění operací přes registry
- **Auto-detekce**: Registry může automaticky detekovat resource z `operation_id`

Registry poskytuje jednotné rozhraní pro exploraci a spouštění všech dostupných služeb, resources a operací v systému.
