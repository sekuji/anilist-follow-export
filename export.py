import os
import requests
import json

url = 'https://graphql.anilist.co'

# Get user ID from user input, validate that it's a positive integer
while True:
    try:
        user_id = int(input("Enter the user ID: "))
        if user_id > 0:
            break
        else:
            print("Please enter a positive integer for the user ID.")
    except ValueError:
        print("Please enter a valid integer for the user ID.")

# Get export type from user input
while True:
    export_type = input("Enter 'followers' or 'following' to choose what to export: ").lower()
    if export_type in ['followers', 'following']:
        break
    else:
        print("Please enter either 'followers' or 'following'.")

# Get the path to save the files, validate that it's a valid directory
while True:
    output_path = input("Enter the path to save the files: ")
    if os.path.exists(output_path) and os.path.isdir(output_path):
        break
    else:
        print("Please enter a valid directory path.")

# Set the initial page number
page_number = 1

# Set the filename for the output file
output_file = f'{export_type.capitalize()}.txt'

# Make the initial request to get the first page of IDs based on export type
query = f'''
    query ($userId: Int!, $page: Int!) {{
        Page (page: $page) {{
            pageInfo {{
                hasNextPage
            }}
            {export_type} (userId: $userId) {{
                id
            }}
        }}
    }}
'''
variables = {
    'userId': user_id,
    'page': page_number
}
response = requests.post(url, json={'query': query, 'variables': variables})
response_json = response.json()

# Create a list to hold all of the IDs
ids = []

# Loop through all pages until there are no more pages left
while response_json['data']['Page']['pageInfo']['hasNextPage']:
    # Append the IDs from the current page to the list of all IDs
    ids += [str(user['id']) for user in response_json['data']['Page'][export_type]]
    
    # Increment the page number and make a new request for the next page of IDs
    page_number += 1
    variables = {
        'userId': user_id,
        'page': page_number
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    response_json = response.json()

# Append the IDs from the final page to the list of all IDs
ids += [str(user['id']) for user in response_json['data']['Page'][export_type]]

# Create a list of URLs from the list of IDs
urls = [f'https://anilist.co/user/{user_id}/' for user_id in ids]

# Construct the full path for the output file
output_file_path = os.path.join(output_path, output_file)

# Write the URLs to the output file
with open(output_file_path, 'w') as f:
    f.write('\n'.join(urls))

print(f'{len(urls)} URLs saved to {output_file_path}')
