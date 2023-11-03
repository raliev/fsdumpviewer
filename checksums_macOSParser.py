from structure_manipulations import add_size_to_all_folders, remove_last_folder, get_last_element;
import re;

#MAC OS X :
#find . -type f -print0 | xargs -0 -P$(sysctl -n hw.ncpu) -n10 shasum -a 256 > ~/checksums.txt
def parse_line(line):

    line_match = re.match(r'^([a-zA-Z0-9]+)  (.*)$', line);
    if line_match:
        checksum = line_match.group(1)
        filepath = line_match.group(2)

        filename = get_last_element(filepath);
        current_path = remove_last_folder(filepath);

        return current_path, filename, checksum ;
    raise "The format is not proper";

def preprocessStructure(input_text):
    lines = input_text.split('\n')

    directories = {}  # Storing directory information

    current_path = None
    shortest_path = None
    for line in lines:
        if line is None:
            continue;
        line = line.strip()
        if line == "":
            continue;
        current_path, filename, checksum = parse_line(line)

        if current_path not in directories:
            directories[current_path] = {'files': {}, 'size': 0}

        if directories[current_path].get('files') is None:
            directories[current_path]['files'] = {};
        if directories[current_path]['files'].get(filename) is None:
            directories[current_path]['files'][filename] = {};

        permissions = directories[current_path]['files'][filename].get('permissions');
        if permissions is None:
            permissions = "-rw-r--r--@";

        directories[current_path]['files'][filename] = {
            'filename': filename,
            'size': 0,
            'date': "",
            'selected': 0,
            'autoselected' : 0,
            'childselected' : 0,
            'permissions': "-rw-r--r--@",
            'selectedSpecialMark' : 0,
            'checksum' : checksum
        }

        add_directories(directories, current_path);

    shortest_path = "./";

    return shortest_path, directories

def add_directories(directories, current_path):
    # Разделите текущий путь на части
    parts = current_path.split('/')

    temp_path = "./"

    for part in parts:
        if part:
            if part == ".":
                temp_path = "./";
                continue;
            filename = part;
            if directories.get(temp_path) is None:
                directories[temp_path] = {};
            if directories[temp_path].get('size') is None:
                directories[temp_path]['size'] = 0;
            if directories[temp_path].get('files') is None:
                directories[temp_path]['files'] = {};
            if directories[temp_path]['files'].get(part) is None:
                directories[temp_path]['files'][part] = {};
            if directories[temp_path]['files'][part].get('permissions') is None:
                directories[temp_path]['files'][part]['permissions'] = "drw-r--r--@";
            if directories[temp_path]['files'][part].get('filename') is None:
                directories[temp_path]['files'][part]['filename'] = filename;
            if directories[temp_path]['files'][part].get('size') is None:
                directories[temp_path]['files'][part]['size'] = 0;
            if directories[temp_path]['files'][part].get('date') is None:
                directories[temp_path]['files'][part]['date'] = 0;
            if directories[temp_path]['files'][part].get('selected') is None:
                directories[temp_path]['files'][part]['selected'] = 0;
            if directories[temp_path]['files'][part].get('childselected') is None:
                directories[temp_path]['files'][part]['childselected'] = 0;
            if directories[temp_path]['files'][part].get('autoselected') is None:
                directories[temp_path]['files'][part]['autoselected'] = 0;
            if directories[temp_path]['files'][part].get('selectedSpecialMark') is None:
                directories[temp_path]['files'][part]['selectedSpecialMark'] = 0;
            temp_path += part
            temp_path += "/"
