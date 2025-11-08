class FormBuilder:
    def __init__(self, path):
        self.path = path

    def create_form(self, action="#", method="POST", inputs=None):
        if inputs is None:
            inputs = [{"type": "text", "name": "username"}]

        form_html = f'<form action="{action}" method="{method}">\n'
        for inp in inputs:
            form_html += f'  <input type="{inp["type"]}" name="{inp["name"]}" placeholder="{inp["name"].capitalize()}">\n'
        form_html += '  <button type="submit">ارسال</button>\n</form>'

        return form_html