import importlib.metadata

for dist in importlib.metadata.distributions():
    req = dist.metadata.get('Requires-Python')
    if req:
        print(f"{dist.metadata['Name']}: {req}")
