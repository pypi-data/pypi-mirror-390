from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class File:
    '''Immutable in-memory file model.

    This class stores file content and metadata in a read-only manner. Use
    the ``stream()`` helper to obtain a readable ``io.BytesIO`` view when a
    file-like object is needed.

    Attributes:
        data (bytes): Raw binary contents of the file. Stored as immutable bytes.
        mime_type (str): The file\'s MIME type (e.g., "text/plain", "image/png").
        filename (str | None): The filename of the file.
        file_path (str | None): The file path of the file.
    '''
    data: bytes
    mime_type: str
    filename: str | None = ...
    filepath: str | None = ...
    def __post_init__(self) -> None:
        """Validate and normalize fields after initialization.

        Raises:
            TypeError: If ``data`` is not bytes-like.
        """
    @property
    def size(self) -> int:
        """Get the size of the file in bytes.

        Returns:
            int: Size of the file in bytes.
        """
    @classmethod
    def from_bytes(cls, data: bytes, filename: str | None = None, filepath: str | None = None) -> File:
        """Creates an File from bytes.

        Args:
            data (bytes): The bytes of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                The filename will be derived from the file path.
            filepath (str | None, optional): The file path of the file. Defaults to None,
                The filename will be derived from the file path.

        Returns:
            File: The instantiated File.
        """
