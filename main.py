from foundry_local_sdk import Configuration, FoundryLocalManager

def main():
    print("Starting Foundry Client...")

    # 1. Konfigürasyon ve başlatma
    try:
        config = Configuration(app_name="FoundryClientApp")
        FoundryLocalManager.initialize(config)
        manager = FoundryLocalManager.instance
    except Exception as e:
        print(f"Failed to initialize Foundry Local SDK: {e}")
        return

    # 2. Kullanılacak model
    model_name = "phi-3.5-mini"
    print(f"Preparing model '{model_name}'...")

    model = None

    try:
        manager.download_and_register_eps()

        catalog = manager.catalog
        model = catalog.get_model(model_name)

        if model is None:
            aliases = [m.alias for m in catalog.list_models()]
            print(f"Model '{model_name}' not found. Available aliases: {aliases[:20]}")
            return

        if not getattr(model, "is_cached", False):
            print(f"Downloading model '{model_name}'...")
            model.download()

        print("Loading model...")
        model.load()

        client = model.get_chat_client()
        response = client.complete_chat([
            {"role": "system", "content": "You are a helpful and friendly AI assistant."},
            {"role": "user", "content": "Hello, world! Can you complete this greeting?"}
        ])

        print("\n" + "=" * 50)
        print("Response from Foundry Client:")
        print("=" * 50)
        print(response.choices[0].message.content)
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if model is not None:
            try:
                model.unload()
            except Exception:
                pass


if __name__ == "__main__":
    main()