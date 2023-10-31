def upload_attachments(ticket_id, attachments,origin_path, approvals_id, auth_user, auth_pass, url, endpoint_attach):
    import requests

    def get_id(link):
        return (link.split("id=",1)[1])

    list_of_files = attachments.split(", ")
    ids_list = list(map(get_id,list_of_files))

    print("\n(1) Ctrl Click the following links to download them:\n")

    for i in ids_list:
        print("https://drive.google.com/uc?export=download&id=" + i)

    x = 'y'
    local_list_of_files = []
    while x != 'n':
        file_string = input("\nAnd then (2) input a local list of file names from your Download folder: ")
        local_list_of_files.append(file_string)
        x = input("Do you have another file? Press Enter or n for No: ")

    def post_file(path,id):
        #"C:\\Users\\nhagl\\Downloads\\"
        full_path = origin_path + path
        file = open(full_path, 'rb')
        files = {
            'file1': file,
        }

        payload_attach = {
            "id": id
        }
        requests.post(f"{url}{endpoint_attach}",auth=(auth_user, auth_pass),files=files, data=payload_attach)

    for p in local_list_of_files:
        try:
            post_file(p,ticket_id)
            post_file(p,approvals_id)
        except FileNotFoundError:
            print("\nCould not upload the following (please upload manually): " + p)