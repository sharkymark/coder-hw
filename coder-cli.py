import os
import json
import requests

coder_url = os.environ['CODER_URL']
coder_session_token = os.environ['CODER_SESSION_TOKEN']
coder_api_route = os.environ['CODER_API_ROUTE']
coder_org_id = os.environ['CODER_ORG_ID']
headers = {"Coder-Session-Token": coder_session_token}

def mask_token(token):
    """Masks the middle characters of a token, revealing first 4 and last 4."""
    mask_length = len(token) - 8  # Calculate mask length based on desired reveal
    return f"{token[:4]}{'*' * mask_length}{token[-4:]}"


def process_response(response, action):
  """
  This function handles successful responses by parsing JSON and printing data,
  and handles errors by printing error messages.
  """
  if response.status_code == 200:

    try:
      # Parse the JSON response (assuming successful response)
      data = response.json()

        # Extract specific data points based on action
      if action.lower() == 'ui':
        username = data.get('username')
        email = data.get('email')
        organizations = data.get('organization_ids', {})
        last_seen = data.get('last_seen_at')
        created_at = data.get('created_at')
        roles = data.get('roles', {})
        role_names = [role.get('name') for role in roles] if roles else []
        
        print(f"\nUsername: {username}")
        print(f"Email: {email}")
        print(f"Organization IDs: {', '.join(organizations) if organizations else 'None'}")
        print(f"Last Seen: {last_seen} | Created At: {created_at}")        
        print(f"Roles: {', '.join(role_names)}")  # Print comma-separated role names

      elif action.lower() == 'lt':
        # Iterate through templates and extract desired data
        for template in data:
          name = template.get('name')
          description = template.get('description')
          created_at = template.get('created_at')
          # ... Extract other data points
          print(f"\nName: {name}")
          print(f"Description: {description}")
          print(f"Created At: {created_at}")


      # Use pretty print to display the JSON data
      #print(json.dumps(data, indent=4))

    except json.JSONDecodeError:
      print("Error: Failed to parse JSON response.")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)

def main():

    while True:
        try:

            print("\x1b[5 q")

            print("\n=============================================================")
            print("This is a simple CLI to interact with a Coder CDE deployment!")
            print("=============================================================\n")

            action = input("""Enter:
            'lt' to list templates,
            'ui' to list authenticated user info
            'ev' to list environment variables
            'q' to exit:
            
            """)

            if action.lower() == 'q':
                print("\n\nExiting...\n\n")
                break

            elif action.lower() == 'ev':
                print("\n\nListing environment variables...\n\n")
                print(f"CODER_URL: {coder_url}")
                masked_token = mask_token(coder_session_token)
                print(f"CODER_SESSION_TOKEN: {masked_token}")
                print(f"CODER_API_ROUTE: {coder_api_route}")
                print(f"CODER_ORG_ID: {coder_org_id}")

            elif action.lower() == 'ui':

                # Construct the API endpoint URL
                api_url = f"{coder_url}/{coder_api_route}/users/me"

                # Send the GET request
                response = requests.get(api_url, headers=headers)

                # Process the response
                if response.status_code == 200:
                    print(f"\nAuthenticated user info:")
                    process_response(response, action)
                else:
                    print("Error:", response.status_code)
                    print("Error:", response.text)

            elif action.lower() == 'lt':

                # Construct the API endpoint URL
                api_url = f"{coder_url}/{coder_api_route}/organizations/{coder_org_id}/templates"

                # Send the GET request
                response = requests.get(api_url, headers=headers)

                # Process the response
                if response.status_code == 200:
                    print(f"\nTemplates:")
                    process_response(response, action)
                else:
                    print("Error:", response.status_code)
                    print("Error:", response.text)
            else:
                print("Invalid action. Please choose a valid option.")
            

        except KeyboardInterrupt:
            print("\n\nExiting...\n\n")
            break

if __name__ == "__main__":
    main()