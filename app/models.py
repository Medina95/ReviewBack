class Review:
    def __init__(self, id, name, content, score):
        self.id = id
        self.name = name
        self.content = content
        self.score = score

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "score": self.score
        }