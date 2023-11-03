from structure_manipulations import get_last_element, remove_last_folder


def compare(roota, rootb, a, b, config):
    def file_compare(file_a, file_b):
        if config.get('compare_names'):
            if file_a['filename'] != file_b['filename']:
                return False
        if config.get('compare_sizes'):
            if file_a['size'] != file_b['size']:
                return False
        if config.get('compare_dates'):
            if file_a['date'] != file_b['date']:
                return False
        if config.get('compare_checksums') :
            if file_a.get('checksum') is not None and file_b.get('checksum') is not None:
                if file_a['checksum'] != file_b['checksum']:
                    return False
        # Here we could add 'compare_checksums' and other comparisons if needed
        return True

    def set_selected(files):
        for filename in files:
            if config.get('compare_specialmark'):
                files[filename]['selectedSpecialMark'] = 1
            else:
                files[filename]['selected'] = 1

    # checking all from a
    for current_path in a:
        current_path_for_b = current_path.replace(roota, rootb, 1) if current_path.startswith(roota) else current_path
        if current_path_for_b not in b:
            set_selected(a[current_path]['files'])
        else:
            for filename, file_info in a[current_path]['files'].items():
                file_b = b[current_path_for_b]['files'].get(filename)
                if not file_b or not file_compare(file_info, file_b):
                    if config.get('compare_specialmark'):
                        file_info['selectedSpecialMark'] = 1
                    else:
                        file_info['selected'] = 1

    # checking all from b
    for current_path in b:
        current_path_for_a = current_path.replace(rootb, roota, 1) if current_path.startswith(rootb) else current_path
        if current_path_for_a not in a:
            set_selected(b[current_path]['files'])
        else:
            for filename, file_info in b[current_path]['files'].items():
                file_a = a[current_path_for_a]['files'].get(filename)
                if not file_a or not file_compare(file_info, file_a):
                    if config.get('compare_specialmark'):
                        file_info['selectedSpecialMark'] = 1
                    else:
                        file_info['selected'] = 1

    # Function mark_parents is assumed to be defined elsewhere
    mark_parents(a)
    mark_parents(b)

    return a, b



def mark_parents(directories):
    for current_path in directories:
        for filename, file_info in directories[current_path]['files'].items():
            if file_info['selected'] == 1 or file_info['selectedSpecialMark'] == 1:
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