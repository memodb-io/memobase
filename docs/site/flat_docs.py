import os
import glob
from pathlib import Path


def read_mdx_files_recursively(directory="."):
    """
    Recursively read all MDX files in the given directory and concatenate them
    with their relative paths.

    Args:
        directory (str): The directory to search in (default: current directory)

    Returns:
        str: Concatenated content of all MDX files with their relative paths
    """
    result = []

    # Use glob to find all .mdx files recursively
    mdx_pattern = os.path.join(directory, "**", "*.mdx")
    mdx_files = glob.glob(mdx_pattern, recursive=True)

    # Sort files for consistent output
    mdx_files.sort()

    for file_path in mdx_files:
        # Get relative path from current directory
        rel_path = os.path.relpath(file_path, directory)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Add file header with relative path
            result.append(f"=== {rel_path} ===\n")
            result.append(content)
            result.append("\n\n")

        except Exception as e:
            print(f"Error reading {rel_path}: {e}")
            result.append(f"=== {rel_path} ===\n")
            result.append(f"Error reading file: {e}\n\n")

    return "".join(result)


def main():
    """Main function to execute the script"""
    print("Reading all MDX files recursively...")

    # Read all MDX files
    concatenated_content = read_mdx_files_recursively()

    if concatenated_content.strip():
        print(
            f"Found and processed MDX files. Total length: {len(concatenated_content)} characters"
        )

        # Save to DOC.md file
        output_file = "DOC.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(concatenated_content)
        print(f"Content saved to {output_file}")

        # Also print to console (you can comment this out if output is too large)
        print("\n" + "=" * 50)
        print("CONCATENATED CONTENT:")
        print("=" * 50)
        print(concatenated_content)

    else:
        print("No MDX files found in the current directory and its subdirectories.")


if __name__ == "__main__":
    main()
