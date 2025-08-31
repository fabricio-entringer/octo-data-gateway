def register_processor(processors: list, processor_class: type):
    try:
        if not any(isinstance(proc, processor_class) for proc in processors):
            processor = processor_class()
            processors.append(processor)
            print(f">>> ✅ \033[95m\033[1m{processor.get_source_name()}\033[0m processor registered successfully.")
        else:
            print(f">>> ⚠️  \033[95m\033[1m{processor_class.__name__}\033[0m processor is already registered.")
    except Exception as e:
        print(f">>> ❌ Failed to register \033[95m\033[1m{processor_class.__name__}\033[0m processor: {e}")