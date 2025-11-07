import argparse
from . import generate_file, dirpath

def generate_plugin(name_plugin, export_folder="."):
    name = name_plugin.lower()
    # Generate plugin header file
    generate_file(f"{export_folder}/plugins/{name}/{name}_plugin.hpp",
                  dirpath + "/templates/plugin_header.jinja",
                  name_plugin=name_plugin)

    # Generate plugin source file
    generate_file(f"{export_folder}/plugins/{name}/{name}_plugin.cu",
                  dirpath + "/templates/plugin_src.jinja",
                  name_plugin=name_plugin)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--plugin_name", type=str, help="Name of the plugin you want to create.", required=True)
    parser.add_argument("-f", "--export_folder", type=str, help="Path to the folder where to place the plugin.", default=".")
    args = parser.parse_args()

    generate_plugin(args.plugin_name, args.export_folder)
