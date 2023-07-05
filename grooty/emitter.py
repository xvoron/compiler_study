class Emitter:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.header = ""
        self.code = ""
    
    def emit(self, code: str):
        self.code += code

    def emit_line(self, code: str):
        self.code += code + "\n"
    
    def header_line(self, code: str):
        self.header += code + "\n"

    def write_file(self):
        with open(self.file_path, 'w') as f:
            f.write(self.header + self.code)
