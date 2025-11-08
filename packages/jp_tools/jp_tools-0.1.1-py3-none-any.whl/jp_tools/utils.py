import requests
from tqdm import tqdm


def download(url: str, filename: str, verify: bool = True) -> None:
    """
    Pulls a file from a URL and saves it in the filename. Used by the class to pull external files.

    Parameters
    ----------
    url: str
        The URL to pull the file from.
    filename: str
        The filename to save the file to.
    verify: bool
        If True, verifies the SSL certificate. If False, does not verify the SSL certificate.

    Returns
    -------
    None
    """
    chunk_size = 10 * 1024 * 1024

    with requests.get(url, stream=True, verify=verify) as response:
        total_size = int(response.headers.get("content-length", 0))

        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading",
        ) as bar:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        bar.update(
                            len(chunk)
                        )  # Update the progress bar with the size of the chunk
