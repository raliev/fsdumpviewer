from structure_manipulations import add_size_to_all_folders;
import re;
def parse_line(line):

    #09/18/2023  02:30 PM             5,927 ParserList.test.js
    #09/18/2023  02:30 PM               358 ParsingError.js
    #09/18/2023  02:30 PM               878 ParsingError.test.js
    #09/18/2023  02:30 PM    <DIR>          pdb

    date = None
    time = None
    size = None
    filename = None

    # Проверяем, является ли первое "слово" корректной датой
    date_match = re.match(r'(\d{2}[\.\/]\d{2}[\.\/]\d{4})', line)
    if date_match:
        date = date_match.group(1)
        line = line[len(date):].strip()

    # Проверяем, является ли следующее "слово" временем

    time_match = re.match(r'(\d{2}:\d{2} [A|P]M)', line)
    if time_match:
        time = time_match.group(1)
        line = line[len(time):].strip()  # Удаляем найденное время из строки

    time_match = re.match(r'(\d{2}:\d{2})', line)
    if time_match:
        time = time_match.group(1)
        line = line[len(time):].strip()  # Удаляем найденное время из строки

    # Проверяем, начинается ли следующее "слово" с "<" или с цифры
    size_match = re.match(r'(\d+([ÿ,\.]*\d+)*)', line)
    if size_match:
        sizeStr = re.sub(r'\D', '', size_match.group(1));
        if (sizeStr is not None):
            size = sizeStr #leaving only numbers
            #size = int(.replace('ÿ', '').replace(',', '').replace('.', '').replace(' ', ''))
            line = line[len(size_match.group(1)):].strip()  # Удаляем найденный размер из строки
            print ("size="+str(size))
        else:
            size = "0";
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
    shortest_path = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"^[\t ]*[\d,\.]+ File\(s\)[ \t]+[\d,\.]+ bytes", line):
            continue
        if re.match(r"^[\t ]*[\d,\.]+ Dir\(s\)[ \t]+[\d,\.]+ bytes", line):
            continue
        if line.startswith("Total Files Listed:"):
            continue
        # Check if it's a directory
        if line.strip().startswith("Directory of"):
            current_path = line.split("Directory of")[1].strip()
            current_path = convertpathfromWindows(current_path)
            if shortest_path is None or len(shortest_path) > len(current_path):
                shortest_path = current_path;
            #print("convertedpath="+current_path)
            directories[current_path] = {'files': {}, 'size': 0}
            continue

        # Check if it's a file

        print("line to parse:" + line)
        date, time, size, filename = parse_line(line)
        print("parsed: ")
        print(date);
        print(time);
        print(size);
        print(filename);

        if current_path not in directories:
            directories[current_path] = {'files': {}, 'size': 0}

        if (size != "<DIR>"):
            if filename != ".." and filename != ".":
                print("directories["+current_path+"]["+filename+"] is set as FILE; size="+size)

                directories[current_path]['files'][filename] = {
                    'filename': filename,
                    'size': int(size),
                    'date': f"{date} {time}",
                    'selected': 0,
                    'autoselected' : 0,
                    'childselected' : 0,
                    'permissions': "-rw-r--r--@",
                    'selectedSpecialMark' : 0
                }

                add_size_to_all_folders(directories, current_path, size)

        else:
            if filename != ".." and filename != ".":
                print("directories["+current_path+"]["+filename+"] is set as DIR")

                directories[current_path]['files'][filename] = {
                    'filename': filename,
                    'size': 0,
                    'date': f"{date} {time}",
                    'selected': 0,
                    'autoselected' : 0,
                    'childselected' : 0,
                    "permissions": "drw-r--r--@",
                    'selectedSpecialMark' : 0
                }


    add_to_structure(directories, shortest_path)

    if (len(directories) == 0):
        raise Exception("this is not a Windows format. No data was read if attempted")

    return shortest_path, directories


def add_to_structure(directories, path):
    components = path.strip('/').split('/')  # Разделение пути на компоненты
    current_path = ""
    for i, component in enumerate(components):
        if i == 0:
            current_path = components[0] + "/"
            componentY = components[1]
        elif (i != len(components) - 1):
            current_path = "/".join(components[0:i+1]) + "/"
            componentY = components[i+1]
        else:
            continue;

        directories.setdefault(current_path, {'files': {}})

        if componentY:  # Если componentY существует, добавляем его в структуру
            print("directories["+current_path+"]['files']["+componentY+"]=");
            print({
                'filename': componentY,
                'size': 0,
                'date': "",
                'selected': 0,
                'autoselected': 0,
                'childselected': 0,
                "permissions": "drw-r--r--@",
                'selectedSpecialMark' : 0
            });
            if directories[current_path].get('files') is None:
                directories[current_path]['files'] = {};
            directories[current_path]['files'][componentY] = {
                'filename': componentY,
                'size': 0,
                'date': "",
                'selected': 0,
                'autoselected': 0,
                'childselected': 0,
                "permissions": "drw-r--r--@",
                'selectedSpecialMark' : 0
            }