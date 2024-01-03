def update_voice_labels(voice_id, name, labels):
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/edit"

    # Convert the labels dictionary to a JSON string
    labels_str = json.dumps(labels)

    # Create a dictionary for the 'files' parameter
    files = {
        'name': (None, name),
        'labels': (None, labels_str),
    }
    # Define the headers for the request
    headers = {
        'xi-api-key': os.getenv("ELEVENLABS_API_KEY")
    }

    response = requests.post(url, files=files, headers=headers)

    return response.text

def update_multiple_voice_labels(voices):
    for voice in voices:
        print(update_voice_labels(voice["voice_id"], voice["name"], voice["labels"]))

# Test the function with a URL
if __name__ == "__main__":
    
    #print(update_voice_labels("wvWbdZLk0IRhDp9WDPqM", "Kloontje", {"type": "fun"}))
    #save_cloned_voices_labels()

    voicelabels = [
    {
        "voice_id": "1kNrDYEnJHvrOpbsa0r6",
        "name": "TourTimmmermans",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "6tlrf8kJqZ4Gev1Y1fX3",
        "name": "Alexander",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "8yzFzqrBLEkfe6zj9tT4",
        "name": "Alexpoki",
        "labels": {
            "type": "poki"
        }
    },
    {
        "voice_id": "C4wUwL9T1zRk3jyvXskw",
        "name": "TwoMinutes",
        "labels": {
            "type": "academic"
        }
    },
    {
        "voice_id": "FiugCfL2Gbnicjj8Un2h",
        "name": "Wietse",
        "labels": {
            "type": "poki"
        }
    },
    {
        "voice_id": "GCJHI2E5HTX83nMCzUPd",
        "name": "Gunther",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "HelwDHA0gu2FM2Nts0Xw",
        "name": "KloontjeZingt",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "PIpnKISoU0pJEeZu0rOq",
        "name": "Theo",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "QsGZEmeRmCjfxtbeF2MJ",
        "name": "Programmer",
        "labels": {
            "type": "anderetijden"
        }
    },
    {
        "voice_id": "TWkhS69Wp7EUWbN09j0E",
        "name": "TourJeanLuc",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "UftcD74Or0buOs8afrHx",
        "name": "AlexanderLach",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "W12we7RY2Sk3Cd5GIuNw",
        "name": "Atje",
        "labels": {
            "type": "doc"
        }
    },
    {
        "voice_id": "ZXTyVq3DzljAKBemwgNj",
        "name": "Bol",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "ZkZC6OWu0rzKfiH2SiTk",
        "name": "Chriet",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "bO9id5YmeU3AVcWKE0gh",
        "name": "Mol",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "c0sJhyHX48T4wsNr9LAf",
        "name": "Wuyts_Museeuw",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "cRDm7TJasAa2jGIXa7IA",
        "name": "EJ",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "d2qbweRLyzgLCmf4sQQz",
        "name": "Rop",
        "labels": {
            "type": "anderetijden"
        }
    },
    {
        "voice_id": "ghFQpmscxzBre3qPrv17",
        "name": "Wuyts Luid",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "mLWvdg03QyZ8e9uGp37I",
        "name": "McLuhan",
        "labels": {
            "type": "academic"
        }
    },
    {
        "voice_id": "nABDziw02UwuwbALfNqC",
        "name": "Frank",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "nUKTda5gnRXEOVVcGquV",
        "name": "Erik",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "oKpnU36sEDiE9trioRXi",
        "name": "Tourheli",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "og4Z66Uck64pzs251d8O",
        "name": "Marleen",
        "labels": {
            "type": "pom"
        }
    },
    {
        "voice_id": "pMikxrtSTkFoa3lMbjNO",
        "name": "TourKoomen",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "pwjWtFIo1HcQyUU5UG96",
        "name": "Yvon",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "qb8TmepHBFTnyZvpLxGL",
        "name": "Wuyts",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "sCFhQBVqv3j4rFJ5ABC6",
        "name": "TourMotor",
        "labels": {
            "type": "tourflits"
        }
    },
    {
        "voice_id": "wRGWRThmqx6ujr4r2bmV",
        "name": "Hansonzeker",
        "labels": {
            "type": "fun"
        }
    },
    {
        "voice_id": "wvWbdZLk0IRhDp9WDPqM",
        "name": "Kloontje",
        "labels": {
            "type": "fun"
        }
    }
]
    #update_multiple_voice_labels(voicelabels)