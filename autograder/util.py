from werkzeug.datastructures import FileStorage

def check_file_validity (file: FileStorage, maxFileSize: int, allowedFileNames: set) -> bool:
    """
    Checks if file passes both extension and max file size test. 
    """
    if file.content_length > maxFileSize:
        return False
    if not file.filename in allowedFileNames:
        return False
    return True

def uniquename_from_email(email: str) -> bool:
    """
    Strips the unique name from an email address given an email.

    Ex: weilez@umich.edu -> weilez
    """
    return email.split('@')[0]