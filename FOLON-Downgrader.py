import argparse
import os
import Utility as Util


def directory(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError(
            '"{}" is not an existing directory'.format(raw_path)
        )
    return os.path.abspath(raw_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A Fallout 4 downgrader application by Team FOLON"
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        metavar="",
        type=directory,
        help="Path to steam(The directory containing a Fallout4.exe file)",
    )
    parser.add_argument(
        "-l",
        "-L",
        "--linux",
        "--Linux",
        help="Use commandline mode (For linux mostly).",
        action="store_true",
    )
    args = parser.parse_args()

    if args.linux:
        from LinuxDowngrader import Linux

        Linux()
    elif args.path:
        import WindowsDowngrader

        Settings = Util.Read_Settings()
        Settings["Steps"] = 3
        Util.Write_Settings(Settings)
        WindowsDowngrader.Windows(args.path)
    else:
        import WindowsDowngrader

        Settings = Util.Read_Settings()
        Settings["Steps"] = 4
        Util.Write_Settings(Settings)
        WindowsDowngrader.Windows()
