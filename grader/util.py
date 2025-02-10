import urllib.request
import json

class Message:
    def __init__(self, email: str, checkpoint: int, url: str):
        self.email = email
        self.checkpoint = checkpoint
        self.url = url
    
    @staticmethod
    def from_json(json_str: str):
        data = json.loads(json_str)
        return Message(
            email=data['email'],
            checkpoint=data['checkpoint'],
            url=data['url']
        )


def download_checkpoint(url: str, name: str):
    """
    Download the checkpoint file from the given URL, name it as the given name.

    Args:
        url (str): The URL to download the checkpoint file from.
    """
    urllib.request.urlretrieve(url, name)
    print(f"File downloaded from {url} to {name}.")



if __name__ == "__main__":
    url = "https://ztabaafahvxlvhoejunj.supabase.co/storage/v1/object/sign/checkpoints/weilez_checkpoint0.ipynb?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGVja3BvaW50cy93ZWlsZXpfY2hlY2twb2ludDAuaXB5bmIiLCJpYXQiOjE3MzgyODc3OTMsImV4cCI6MTc0MzQ3MTc5M30.B60Np9_kJhK87PMiFyzR-SLxFDer_HRaYsHgB9t1w1Y&download=weilez_checkpoint0.ipynb"
    download_checkpoint(url, "weilez_checkpoint0.ipynb")