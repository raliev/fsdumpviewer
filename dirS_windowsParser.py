from structure_manipulations import add_size_to_all_folders;

def parse_line(line):
    # Инициализируем выходные значения
    date = None
    time = None
    size = None
    filename = None

    # Проверяем, является ли первое "слово" корректной датой
    date_match = re.match(r'(\d{2}\.\d{2}\.\d{4})', line)
    if date_match:
        date = date_match.group(1)
        line = line[len(date):].strip()  # Удаляем найденную дату из строки

    # Проверяем, является ли следующее "слово" временем
    time_match = re.match(r'(\d{2}:\d{2})', line)
    if time_match:
        time = time_match.group(1)
        line = line[len(time):].strip()  # Удаляем найденное время из строки

    # Проверяем, начинается ли следующее "слово" с "<" или с цифры
    size_match = re.match(r'(\d+([ÿ\s]*\d+)*)', line)
    if size_match:
        size = int(size_match.group(1).replace('ÿ', '').replace(' ', ''))
        line = line[len(size_match.group(1)):].strip()  # Удаляем найденный размер из строки
    elif line.startswith("<DIR>"):
        size = "<DIR>"
        line = line[len(size):].strip()  # Удаляем <DIR> из строки

    # Оставшаяся часть строки - это имя файла/папки
    filename = line

    return date, time, size, filename

def convertpathfromWindows(path):
    path = path.replace("\\", "/")

    if len(path) > 1 and path[1] == ":":
        path = path[0].lower() + path[1:]

    return path + "/"



def preprocessStructureWindows(input_text):
    lines = input_text.split('\n')

    directories = {}  # Storing directory information

    current_path = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if it's a directory
        if line.strip().startswith("Directory of"):
            current_path = line.split("Directory of")[1].strip()
            current_path = convertpathfromWindows(current_path)
            #print("convertedpath="+current_path)
            directories[current_path] = {'files': {}, 'size': 0}
            continue

        # Check if it's a file
        date, time, size, filename = parse_line(line)

        if current_path not in directories:
            directories[current_path] = {'files': {}, 'size': 0}

        if (size != "<DIR>"):

            #print("directories["+current_path+"]["+filename+"] is set as DIR")

            directories[current_path]['files'][filename] = {
                'filename': filename,
                'size': int(size),
                'date': f"{date} {time}",
                'selected': 0,
                'autoselected' : 0,
                'childselected' : 0,
                'permissions': "-rw-r--r--@"
            }

            add_size_to_all_folders(directories, current_path, size)

        else:
            #print("directories["+current_path+"]["+filename+"] is set as FILE")

            directories[current_path]['files'][filename] = {
                'filename': filename,
                'size': 0,
                'date': f"{date} {time}",
                'selected': 0,
                'autoselected' : 0,
                'childselected' : 0,
                "permissions": "drw-r--r--@"
            }



    return directories