class EmailFixer:
    @staticmethod
    def fix(email: str) -> str:
        '''
        Do e.x.a.m.p.l.e@gmail.com, etc same as example@gmail.com by removing dot's and ignoring text after '+'.
        Preventing multi-accounts on one gmail.
        '''
        if email.endswith("@gmail.com"):
            local_part, domain = email.split("@")
            local_part = local_part.replace(".", "").split("+")[0]
            return f"{local_part}@{domain}".lower()
        return email
