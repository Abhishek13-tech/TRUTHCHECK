import os


REFERENCE_FOLDER = "datasets/reference_texts"


def load_reference_texts():
    """
    Load all .txt reference files from the reference folder.
    """

    references = []

    if not os.path.exists(REFERENCE_FOLDER):
        return references

    for filename in os.listdir(REFERENCE_FOLDER):

        if filename.endswith(".txt"):

            file_path = os.path.join(
                REFERENCE_FOLDER,
                filename
            )

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read().strip()

            if text:
                references.append({
                    "filename": filename,
                    "text": text
                })

    return references


# Test
if __name__ == "__main__":

    references = load_reference_texts()

    print(f"Reference files found: {len(references)}")

    for reference in references:
        print(f"- {reference['filename']}")