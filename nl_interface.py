from difflib import SequenceMatcher as SM


def get_similarity_score(s1, s2)
	return SM(None, s1, s2).ratio()

commands = {}