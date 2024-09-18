"""
Gets and updates configuration values in the database.

The Configuration table acts like a key-value store.

"""
import core.model as model
import json



def get(config_key, default_config_value=None):
    """
    Returns an object associated with the configuration key. If the key is not
    found, raise KeyError if default_config_value is not set. If
    default_config_value is set, then create the key-value pair in the database
    and return the default_config_value.

    """
    with model.write_lock:
        with model.db:
            try:
                return json.loads(
                    model.Configuration.get(model.Configuration.key == config_key).value
                )
            except model.Configuration.DoesNotExist:
                if default_config_value is None:
                    raise KeyError
                model.Configuration.create(key=config_key, value=json.dumps(default_config_value))
                return default_config_value



def set(config_key, config_value):
    """
    Sets the configuration key to the given value.

    Returns the original config_value.

    """
    config_value_str = json.dumps(config_value)

    with model.write_lock:
        with model.db:
            try:
                model.Configuration.get(model.Configuration.key == config_key)

            except model.Configuration.DoesNotExist:
                # Create the entry because it doesn't exist yet
                model.Configuration.create(key=config_key, value=config_value_str)

            else:
                # Update the entry because it already exists
                model.Configuration.update(value=config_value_str).where(model.Configuration.key == config_key).execute()

    return config_value



def items():
    """
    Returns all key-value pairs in the database.

    """
    with model.db:
        for config in model.Configuration.select():
            yield (config.key, json.loads(config.value))
