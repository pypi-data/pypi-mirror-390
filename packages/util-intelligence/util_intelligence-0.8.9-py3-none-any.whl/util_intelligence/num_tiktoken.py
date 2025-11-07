import tiktoken


def num_tokens_from_messages(messages, model="gpt-4o"):
    """Return the number of tokens used by a list of messages."""

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(messages))
