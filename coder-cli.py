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

def format_roles(roles):
  """
  This function takes a list of roles and returns a comma-separated string
  with proper formatting.
  """
  if not roles:
    return "None"
  role_names = [role.get('name') for role in roles]
  return ", ".join(role_names)

def format_org_ids(org_ids):
  """
  This function takes a list of organization IDs and returns a comma-separated string
  with proper formatting.
  """
  if not org_ids:
    return "None"
  return ", ".join(org_ids)

def format_user_info(user):
  """
  This function formats user information for printing, without date formatting.
  """
  username = user.get('username')
  email = user.get('email')
  roles_formatted = format_roles(user.get('roles', []))
  org_ids_formatted = format_org_ids(user.get('organization_ids', []))
  last_seen = user.get('last_seen_at')
  created_at = user.get('created_at')

  return f"Username: {username}\nEmail: {email}\nRoles: {roles_formatted}\nOrganization Id(s): {org_ids_formatted}\nLast Seen: {last_seen}\nCreated At: {created_at}"


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
          user_data = response.json()
          formatted_user_info = format_user_info(user_data)
          print(formatted_user_info)


      elif action.lower() == 'lu':
        user_data = response.json()
        user_count = user_data.get('count')
        users = user_data.get('users', [])
        formatted_users = [format_user_info(user) for user in users]
        print(f"Total Users: {user_count}\n")
        for user_info in formatted_users:
          print(user_info)  # Print each formatted user information
          print("\n")
          
      elif action.lower() == 'lt':
        # Iterate through templates and extract desired data
        for template in data:
          name = template.get('display_name') + " (" + template.get('name') + ")"
          description = template.get('description')
          created_at = template.get('created_at')
          updated_at = template.get('updated_at')
          active_users = template.get('active_user_count')
          created_by = template.get('created_by_name')
          deprecated = template.get('deprecated')
          # ... Extract other data points
          print(f"\nDisplay(name): {name}")
          print(f"Description: {description}")
          print(f"Created by: {created_by} at: {created_at} updated at: {updated_at}")
          if deprecated:
            print(f"**deprecated**")
          print(f"Active users: {active_users}")

      elif action.lower() == 'lw':
        workspace_data = response.json()
        workspace_count = workspace_data.get('count')
        workspaces = workspace_data.get('workspaces', [])
        print(f"Total workspaces: {workspace_count}\n")
        for workspace in workspaces:
          name = workspace.get('name')
          template_name = workspace.get('template_name')
          template_version = workspace.get('latest_build', {}).get('template_version_name')
          health = workspace.get('health', {}).get('healthy')
          status = workspace.get('latest_build', {}).get('status')
          outdated = workspace.get('outdated', False)
          last_built = workspace.get('latest_build', {}).get('created_at')
          owner = workspace.get('latest_build', {}).get('workspace_owner_name')
          print(f"  Name: {name}")
          print(f"  Owner: {owner}")
          print(f"  Template (version): {template_name} ({template_version})")
          print(f"  Status: {status}") 
          print(f"  Last built: {last_built}") 
          print(f"  Healthy: {health}")

          if outdated:
              print(f"  Deprecated")  # Print 'deprecated' only if 'outdated' is True


          latest_build = workspace.get('latest_build')
          if latest_build:
            resources = latest_build.get('resources', [])
            if resources:
              print("  Apps:")
              for resource in resources:
                agents = resource.get('agents', [])
                for agent in agents:
                  apps = agent.get('apps', [])
                  for app in apps:
                    display_name = app.get('display_name')
                    if display_name:
                      print(f"    - {display_name}")                  
                  display_apps = agent.get('display_apps')
                  if display_apps:
                    for app in display_apps:
                      print(f"    - {app}")

          print()  # Add a new line after each workspace information


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
            'lw' to list workspaces,
            'lu' to list users,
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
                    print(f"\nAuthenticated user info:\n")
                    process_response(response, action)
                else:
                    print("Error:", response.status_code)
                    print("Error:", response.text)

            elif action.lower() == 'lu':

                # Construct the API endpoint URL
                api_url = f"{coder_url}/{coder_api_route}/users"

                # Send the GET request
                response = requests.get(api_url, headers=headers)

                # Process the response
                if response.status_code == 200:
                    print(f"\nUsers:\n")
                    process_response(response, action)
                else:
                    print("Error:", response.status_code)
                    print("Error:", response.text)

            elif action.lower() == 'lw':

                # Construct the API endpoint URL
                api_url = f"{coder_url}/{coder_api_route}/workspaces"

                # Send the GET request
                response = requests.get(api_url, headers=headers)

                # Process the response
                if response.status_code == 200:
                    print(f"\nWorkspaces:\n")
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