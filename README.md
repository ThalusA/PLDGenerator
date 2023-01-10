# PLDGenerator

PLDGenerator is a script for generating EPITECH's EIP Project Log Documents (PLD) in a user-friendly way. It takes in a JSON document that follows a specific schema, as well as your company's primary and secondary logos in PDF format, and generates a LaTeX and PDF document of the PLD in the build folder.

## Requirements

To use PLDGenerator, you will need to have the following files in the assets folder:

- primary_logo.pdf: Your primary logo in the PDF format
- secondary_logo.pdf: Your secondary logo in the PDF format
- pld_data.json: Your PLD document in the form of a JSON file that follows the schema provided in this repository: https://raw.githubusercontent.com/ThalusA/PLDGenerator/master/pld_schema.json

It's also recommended that you have Docker installed on your machine, as PLDGenerator is built to be run as a container. If you do not have Docker installed, you will need to install the LaTeX packages used by the script to build the PLD document.

## Usage

To use PLDGenerator, you can run the following command:

```bash
make release
```

This command will build a Docker container and run the script inside of it. Once the script is done running, you will have your Project Log Document in the form of a LaTeX and PDF document in the build folder. If you are not using Docker and are running the script locally, you can add "sudo" in front of the command to run the script as a superuser.

If you have any question or problem with the script or data feel free to contact the author or open an issue on the repository.
