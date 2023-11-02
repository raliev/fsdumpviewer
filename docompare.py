def compare(a, b):
    # Проверяем все пути и файлы из a
    for current_path in a:
        if current_path not in b:
            # Если путь из a отсутствует в b, выставляем selected:1 для всех файлов из a[current_path]
            for filename in a[current_path]['files']:
                a[current_path]['files'][filename]['selected'] = 1
        else:
            # Если путь присутствует и в a и в b, проверяем все файлы
            for filename in a[current_path]['files']:
                if filename not in b[current_path]['files']:
                    a[current_path]['files'][filename]['selected'] = 1

    # Проверяем все пути и файлы из b
    for current_path in b:
        if current_path not in a:
            # Если путь из b отсутствует в a, выставляем selected:1 для всех файлов из b[current_path]
            for filename in b[current_path]['files']:
                b[current_path]['files'][filename]['selected'] = 1
        else:
            # Если путь присутствует и в a и в b, проверяем все файлы
            for filename in b[current_path]['files']:
                if filename not in a[current_path]['files']:
                    b[current_path]['files'][filename]['selected'] = 1

    mark_parents(a);
    mark_parents(b);

    return a, b

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

def mark_parents(directories):
    for current_path in directories:
        for filename, file_info in directories[current_path]['files'].items():
            if file_info['selected'] == 1:
                parent_path = current_path
                # Если parent_path не корневой каталог
                while parent_path:
                    if parent_path in directories:
                        removed_element = get_last_element(parent_path)
                        parent_path_w_removed_lastitem = remove_last_folder(parent_path);
                        if parent_path == "./":
                            break;
                        if removed_element in directories[parent_path_w_removed_lastitem]['files']:
                            directories[parent_path_w_removed_lastitem]['files'][removed_element]['autoselected'] = 1
                    parent_path = remove_last_folder(parent_path)
                break;
    return directories