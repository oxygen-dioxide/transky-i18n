import glob
import time
import babel
import click
import pathlib
import google.generativeai as genai

gemini_api_key = pathlib.Path("secrets/gemini_api_key.txt").read_text(encoding="utf8")

prompt = pathlib.Path("prompt.txt").read_text(encoding="utf8")

def get_native_language_name(language_code):
    locale = babel.Locale.parse(language_code, sep="-")
    return locale.get_display_name(locale)

def translate(
        input_path:pathlib.Path, 
        output_path:pathlib.Path,
        to_language:str):
    glossary_path = pathlib.Path(to_language)/"glossary.md"
    glossary = glossary_path.read_text(encoding="utf8")
    to_language_name = get_native_language_name(to_language)

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=prompt.format(
            to=to_language,
            glossary=glossary)
    )
    response = model.generate_content(input_path.read_text(encoding="utf8"))
    output_path.write_text(response.text, encoding="utf8")
    print(f"Translated {input_path} to {to_language_name} and saved to {output_path}")
    time.sleep(5)

@click.command()
@click.option('--overwrite', is_flag=True, show_default=True, default=False, help="Overwrite existing files")
@click.argument('glob_pattern', type=str)
def main(overwrite:bool, glob_pattern: str):
    from_lang="zh-cn"
    to_lang="en-us"
    input_folder = pathlib.Path(from_lang)
    output_folder = pathlib.Path(to_lang)
    files = glob.glob(glob_pattern, root_dir=input_folder)
    print(f"Translating {len(files)} files from {from_lang} to {to_lang}")
    for filename in files:
        if((not overwrite) and (output_folder/filename).is_file()):
            print(f"Skipping {filename} as it already exists")
            continue
        translate(
            input_path=input_folder/filename, 
            output_path=output_folder/filename, 
            to_language=to_lang)

if(__name__=="__main__"):
    main()