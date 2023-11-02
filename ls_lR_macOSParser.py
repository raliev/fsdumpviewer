from structure_manipulations import add_size_to_all_folders;
def preprocessStructure(input_text):
    lines = input_text.split('\n')

    directories = {}  # Storing directory information

    simplified_output = []
    current_path = './'
    for line in lines:
        if not line:
            continue
        if line.startswith('./'):
            current_path = line.split(':')[0] + '/'
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        permissions, _, owner, _, size, month, day, *remaining = parts
        year_or_time = remaining[0]

        #print(year_or_time)


        # Проверка на наличие года или времени в строке
        if ':' in year_or_time:
            date = f"{day} {month}"
            remaining = remaining[1:]
        else:
            date = f"{day} {month} {year_or_time}"
            remaining = remaining[1:]

        filename = ' '.join(remaining)

        if current_path not in directories:
            directories[current_path] = {'files': {}, 'size': 0}

        directories[current_path]['files'][filename] = {
            'filename': filename,
            'size': int(size),
            'permissions': permissions,
            'date': date,
            'selected': 0,
            'autoselected' : 0,
            'childselected' : 0
        }

        add_size_to_all_folders(directories, current_path, size)

    return directories