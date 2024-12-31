
# imports
import mwclient  # for downloading example Wikipedia articles
import mwparserfromhell  # for splitting Wikipedia articles into sections
from openai import OpenAI  # for generating embeddings
import os  # for environment variables
import pandas as pd  # for DataFrames to store article sections and embeddings
import re  # for cutting <ref> links out of Wikipedia articles
import tiktoken  # for counting tokens


from Chile import scrape_chile



"""

    
    4. Split long sections into smaller sections
    
    5. Compute embeddings for each chunk
    
    6. Store chunks and embeddings
"""


GPT_MODEL = "gpt-4o-mini"


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def halved_by_delimiter(string: str, delimiter: str = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = num_tokens(string)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]


def truncated_string(
        string: str,
        model: str,
        max_tokens: int,
        print_warning: bool = True,
    ) -> str:
    
    """Truncate a string to a maximum number of tokens."""
    
    encoding = tiktoken.encoding_for_model(model)
    encoded_string = encoding.encode(string)
    truncated_string = encoding.decode(encoded_string[:max_tokens])
    if print_warning and len(encoded_string) > max_tokens:
        print(f"Warning: Truncated string from {len(encoded_string)} tokens to {max_tokens} tokens.")
    return truncated_string


def split_strings_from_subsection(
        subsection: tuple[list[str], str],
        max_tokens: int = 1000,
        model: str = GPT_MODEL,
        max_recursion: int = 5,
    ) -> list[str]:
    
    """
    Split a subsection into a list of subsections, each with no more than max_tokens.
    Each subsection is a tuple of parent titles [H1, H2, ...] and text (str).
    """
    titles, text = subsection
    string = "\n\n".join(titles + [text])
    num_tokens_in_string = num_tokens(string)
    # if length is fine, return string
    if num_tokens_in_string <= max_tokens:
        return [string]
    # if recursion hasn't found a split after X iterations, just truncate
    elif max_recursion == 0:
        return [truncated_string(string, model=model, max_tokens=max_tokens)]
    # otherwise, split in half and recurse
    else:
        titles, text = subsection
        for delimiter in ["\n\n", "\n", ". "]:
            left, right = halved_by_delimiter(text, delimiter=delimiter)
            if left == "" or right == "":
                # if either half is empty, retry with a more fine-grained delimiter
                continue
            else:
                # recurse on each half
                results = []
                for half in [left, right]:
                    half_subsection = (titles, half)
                    half_strings = split_strings_from_subsection(
                        half_subsection,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    results.extend(half_strings)
                return results
    # otherwise no split was found, so just truncate (should be very rare)
    return [truncated_string(string, model=model, max_tokens=max_tokens)]


def get_embeddings(client, document_sections):
    # split sections into chunks
    MAX_TOKENS = 1600
    document_strings = []
    
    # Section = tuple[list[str], str]
    for section in document_sections:
        document_strings.extend(split_strings_from_subsection(section, max_tokens=MAX_TOKENS))

    print(f"{len(document_sections)} Document sections split into {len(document_strings)} strings.")

    EMBEDDING_MODEL = "text-embedding-3-small"
    BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request

    embeddings = []
    for batch_start in range(0, len(document_strings), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = document_strings[batch_start:batch_end]
        print(f"Batch {batch_start} to {batch_end-1}")
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    df = pd.DataFrame({"text": document_strings, "embedding": embeddings})
    return df

def save_doc(df, title):
    # save document chunks and embeddings

    SAVE_PATH = f'data/{title}.csv'

    df.to_csv(SAVE_PATH, index=False)

def generate_embeddings():
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))

    document_sections = scrape_chile.get_data()
    
    df_embeddings = get_embeddings(client, document_sections)
    save_doc(df_embeddings, "Chile/Código Civil")
    
    return df_embeddings
    
