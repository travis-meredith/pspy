


class Settings:

    content_width: int = 120
    content_height: int = 40
    file_name_length: int = 40
    goto_list_width: int = 18

    @classmethod
    def serialise(cls):
        ret = {}
        for key, value in cls.__dict__.items():
            if "__" not in key and "serialise" not in key:
                ret[key] = value
        print(ret)
        return ret

