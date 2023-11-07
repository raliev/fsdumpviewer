from structure_manipulations import add_size_to_all_folders;
def preprocessStructure(input_text):
    lines = input_text.split('\n')

    directories = {}  # Storing directory information

    simplified_output = []
    current_path = './'
    for line in lines:
        if line.startswith(" Directory of "):
            raise Exception("this is not a MacOS/Linux format")
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

        if permissions.startswith('d'):
            size = 0 #we zero size because the number next to the directory name is not actually a size in Kb.

        #print(year_or_time)


        # Проверка на наличие года или времени в строке
        date = f"{day} {month} {year_or_time}"
        remaining = remaining[1:]

        filename = ' '.join(remaining)

        filename = filename.strip();

        if filename.endswith("*"): # win-bash adds it to some files
            filename = filename.rstrip("*");

        if current_path not in directories:
            directories[current_path] = {'files': {}, 'size': 0}

        if filename.endswith("/"): # this is the case for win-bash
            filename = filename.rstrip("/");

        directories[current_path]['files'][filename] = {
            'filename': filename,
            'size': int(size),
            'permissions': permissions,
            'date': date,
            'selected': 0,
            'autoselected' : 0,
            'childselected' : 0,
            'selectedSpecialMark' : 0
        }

        add_size_to_all_folders(directories, current_path, size)

    if (len(directories) == 0):
        raise Exception("this is not a MacOS/Linux format. No data was read if attempted")

    return directories