def pre_process_content(content:str):
    return content.split(" ",maxsplit=1)[0], content.split(" ",maxsplit=1)[1]