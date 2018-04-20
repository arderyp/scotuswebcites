def global_variables(request):
    with open("VERSION.txt", "r") as input_file:
        version = ''.join(input_file.readlines()).strip()
    return {'VERSION': version}