def remove_last_folder(path: str) -> str:
    parts = path.split('/')
    parts = parts[:-2] if parts[-1] == '' else parts[:-1]
    return '/'.join(parts) + '/'

def get_last_element(path: str) -> str:
    parts = path.split('/')
    if parts[-1] == '':
        return parts[-2]
    else:
        return parts[-1]
def add_size_to_all_folders(directories, current_path, size):
    # Разделите текущий путь на части
    parts = current_path.split('/')

    # Инициализируйте временный путь
    temp_path = ""

    # Пройдитесь по каждой части пути
    for part in parts:
        # Если часть пути не пуста (это может быть первой точкой в пути, например, "./a/b/c")
        if part:
            # Добавьте часть к временному пути
            temp_path += part
            if (part != ""):
                temp_path = temp_path + "/";
            # Добавьте size к папке в словаре directories
            if directories.get(temp_path) is None:
                directories[temp_path] = {};
            if directories[temp_path].get('size') is None:
                directories[temp_path]['size'] = 0;

            #print("directories[" +temp_path + "][size] += "+str(size));

            directories[temp_path]['size'] += int(size)


def add_marks_to_all_folders(directories, current_path, incr):
    # Разделите текущий путь на части
    parts = current_path.split('/')

    # Инициализируйте временный путь
    temp_path = ""

    # Пройдитесь по каждой части пути
    for part in parts:
        # Если часть пути не пуста (это может быть первой точкой в пути, например, "./a/b/c")
        if part:
            # Добавьте часть к временному пути
            temp_path += part
            if (part != ""):
                temp_path = temp_path + "/";
            # Добавьте size к папке в словаре directories
            if directories.get(temp_path) is None:
                directories[temp_path] = {};
            if directories[temp_path].get('size') is None:
                directories[temp_path]['childselected'] = 0;

            #print("directories[" +temp_path + "][childselected] += "+str(incr));

            if directories[temp_path].get('childselected') is None:
                directories[temp_path]['childselected']= 0;


            directories[temp_path]['childselected'] += int(incr)