from ls_lR_macOSParser import preprocessStructure as ls_lR_macOSParser_preprocessStructure;
from ls_lR_macOSParser2 import preprocessStructure as ls_lR_macOSParser2_preprocessStructure;
from dirS_windowsParser import preprocessStructureWindows as dirS_windowsParser_preprocessStructure;
def parser(text):
    try:
        print("trying macOS/Linux parser...")
        return "./", ls_lR_macOSParser_preprocessStructure(text);

    except:
        print("macOS parser attempt - failed");
        try:
            print("trying alternative macOS/Linux parser...")
            return "./", ls_lR_macOSParser2_preprocessStructure(text);
        except:
            print("macOS parser2 attempt - failed");
            print("trying windows cms parser...")
            shortest_path, dir = dirS_windowsParser_preprocessStructure(text);
            print("shortest_path="+shortest_path);
            return shortest_path, dir;
            try:
                return dirS_windowsParser_preprocessStructure(text);
            except:
                print("windows cmd parser attempt - failed");
