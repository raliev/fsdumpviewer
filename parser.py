from ls_lR_macOSParser import preprocessStructure as ls_lR_macOSParser_preprocessStructure;
from ls_lR_macOSParser2 import preprocessStructure as ls_lR_macOSParser2_preprocessStructure;
from dirS_windowsParser import preprocessStructureWindows as dirS_windowsParser_preprocessStructure;
from checksums_macOSParser import preprocessStructure as checksums_macOSParser_preprocessStructure;


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
            try:
                return dirS_windowsParser_preprocessStructure(text);
            except:
                print("windows parser2 attempt - failed");
                print("trying checksums parser...")

                return checksums_macOSParser_preprocessStructure(text);


                print("checksums parser attempt - failed");
