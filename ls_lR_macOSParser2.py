from structure_manipulations import add_size_to_all_folders;
def preprocessStructure(input_text):
    lines = input_text.split('\n')

    directories = {}  # Storing directory information

    simplified_output = []
    for line in lines:
        if not line:
            continue
        if line.startswith(" Directory of "):
            raise Exception("this is not a MacOS/Linux format")
        parts = line.split()
        # Проверяем минимальное количество частей, чтобы отсечь неинформативные строки
        if len(parts) < 9:
            continue
        # Пропускаем идентификатор узла файловой системы, номер индексного дескриптора и владельца группы, так как они не требуются
        permissions, _, owner, _, size, month, day, time_or_year, *path_parts = parts[2:]

        # Собираем полный путь и отделяем имя файла
        full_path = ' '.join(path_parts)
        if full_path == ".":
            continue;
        path, filename = full_path.rsplit('/', 1)
        if not path.endswith('/'):
            path += '/'

        if path not in directories:
            directories[path] = {'files': {}, 'size': 0}

        date = f"{day} {month}"
        if ':' not in time_or_year:
            date += f" {time_or_year}"

        directories[path]['files'][filename] = {
            'filename': filename,
            'size': int(size),
            'permissions': permissions,
            'date': date,
            'selected': 0,
            'autoselected' : 0,
            'childselected' : 0
        }

        add_size_to_all_folders(directories, path, int(size))

    return directories