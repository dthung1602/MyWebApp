from Handler import Handler


class Rot13(Handler):
    page_title = "Rot 13"

    @staticmethod
    def rot13(text):
        a = ord('a')
        A = ord('A')
        new_text = ""
        for char in text:
            new_char = char
            if char.isalpha():
                if char.isupper():
                    new_char = chr((ord(char) - A + 13) % 26 + A)
                else:
                    new_char = chr((ord(char) - a + 13) % 26 + a)
            new_text += new_char
        return new_text

    def get(self):
        text = self.request.get("text")
        self.render("rot13.html", text=self.rot13(text))
