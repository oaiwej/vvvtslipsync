from vvvtslipsync.utils.create_pau_mora import create_pau_mora

def extract_moras(query_data: dict):
    moras = []
    pre_phoneme_pau_mora = create_pau_mora(query_data["prePhonemeLength"])
    post_phoneme_pau_mora = create_pau_mora(query_data["postPhonemeLength"])
    moras += [pre_phoneme_pau_mora] + [mora for accent_phrase in query_data["accent_phrases"] 
                for mora in (accent_phrase["moras"] + ([accent_phrase["pause_mora"]] if accent_phrase["pause_mora"] else []))] + [post_phoneme_pau_mora]
    return moras
