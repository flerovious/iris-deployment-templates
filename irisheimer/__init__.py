import os
import shutil

import click


@click.command()
@click.argument("repo", type=str)
def main(repo):
    click.echo(f"Repository: {repo}")

    # Path to the template file
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "aws", "flask", "__main__.py"
    )

    # Path for the new main.py file
    output_path = os.path.join(os.getcwd(), "__main__.py")

    try:
        # Copy the template file to the new location
        shutil.copy2(template_path, output_path)

        # Read the content of the new file
        with open(output_path, "r") as f:
            content = f.read()

        # Replace the placeholder with the actual repository URL
        content = content.replace("{repository_url}", repo)

        # Write the updated content back to the file
        with open(output_path, "w") as f:
            f.write(content)

        click.echo(f"Created Pulumi AWS configuration for Flask in {os.getcwd()}")
        click.echo(f"Install pulumi dependencies with `pip install pulumi pulumi-aws`")
    except IOError as e:
        click.echo(f"Error creating file: {e}", err=True)


if __name__ == "__main__":
    main()
