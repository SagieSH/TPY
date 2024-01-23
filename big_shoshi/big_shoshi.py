import threading, IPython, time, importlib.util, sys, os

WAIT_TIME = 0.1


def get_module_name_from_path(path):
    path = os.path.split(path)
    return path[-1].rstrip(".py")


def load_file(file_path):
    module_name = get_module_name_from_path(file_path)

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # IMPORTANT! Otherwise functions outside this scope will not know this module!
    globals()[module_name] = module


def dynamic_loader(directory):
    last_modified = dict()
    while True:
        time.sleep(WAIT_TIME)
        for file_path in os.listdir(directory):
            # Important since os.listdir returns path relative to the directory
            full_path = os.path.join(directory, file_path)

            # Skip directories.
            if os.path.isdir(full_path):
                continue

            # Load all changed and new files.
            if last_modified.get(full_path, None) != os.path.getmtime(full_path):
                load_file(full_path)


def main():
    assert len(sys.argv) == 2, "Usage: 'python big_shoshi.py <modules_dir>'"

    t = threading.Thread(target=dynamic_loader, args=[sys.argv[1]])
    
    # This is important so the main thread won't have to wait until this thread dies to quit.
    t.daemon = True

    t.start()
    IPython.embed()


if __name__ == "__main__":
    main()