

def register_processor(processors: list, processor_class: type):
    try:
        if not any(isinstance(proc, processor_class) for proc in processors):
            processor = processor_class()
            processors.append(processor)
            print(f"✅ {processor.get_source_name()} processor registered successfully.")
        else:
            print(f"⚠️  {processor_class.__name__} processor is already registered.")
    except Exception as e:
        print(f"❌ Failed to register {processor_class.__name__} processor: {e}")