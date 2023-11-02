from structure_manipulations import get_last_element, remove_last_folder


def compare(roota, rootb, a, b):

    # checking all from a
    for current_path in a:
        current_path_for_b = current_path;
        if current_path.startswith(roota):
            current_path_for_b = rootb + current_path.removeprefix(roota);
        if current_path_for_b not in b:
            # if path from a is not in b, set selected=1 for all files from a[current_path]
            for filename in a[current_path]['files']:
                a[current_path]['files'][filename]['selected'] = 1
        else:
            # If path is in a and b, check all files
            for filename in a[current_path]['files']:
                if filename not in b[current_path_for_b]['files']:
                    a[current_path]['files'][filename]['selected'] = 1

    # checking all from b
    for current_path in b:
        current_path_for_a = current_path;
        if current_path.startswith(rootb):
            current_path_for_a = roota + current_path.removeprefix(rootb);
        if current_path_for_a not in a:
            # if path from b is not in a, set selected=1 for all files from b[current_path]
            for filename in b[current_path]['files']:
                b[current_path]['files'][filename]['selected'] = 1
        else:
            # If path is in a and b, check all files
            for filename in b[current_path]['files']:
                if filename not in a[current_path_for_a]['files']:
                    b[current_path]['files'][filename]['selected'] = 1

    mark_parents(a);
    mark_parents(b);

    return a, b



def mark_parents(directories):
    for current_path in directories:
        for filename, file_info in directories[current_path]['files'].items():
            if file_info['selected'] == 1:
                parent_path = current_path
                while parent_path:
                    print("parent_path=" + parent_path)
                    if parent_path in directories:
                        removed_element = get_last_element(parent_path)
                        parent_path_w_removed_lastitem = remove_last_folder(parent_path);
                        if parent_path == "./":
                            break;
                        if directories.get(parent_path_w_removed_lastitem) is None:
                            break;
                        if directories[parent_path_w_removed_lastitem].get('files') is None:
                            break;
                        if removed_element in directories[parent_path_w_removed_lastitem]['files']:
                            directories[parent_path_w_removed_lastitem]['files'][removed_element]['autoselected'] = 1
                            print("marking directories["+parent_path_w_removed_lastitem+"]['files']["+removed_element+"]['autoselected']");
                    parent_path = remove_last_folder(parent_path)
                break;
    return directories