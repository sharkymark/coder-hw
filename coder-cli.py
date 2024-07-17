import os
import sys
import json
import requests

coder_url = os.environ['CODER_URL']
coder_session_token = os.environ['CODER_SESSION_TOKEN']
coder_api_route = os.environ['CODER_API_ROUTE']
coder_org_id = os.environ['CODER_ORG_ID']
headers = {"Coder-Session-Token": coder_session_token}

def print_environment_variables():
  print("\nListing environment variables...\n\n")
  print(f"CODER_URL: {coder_url}")
  masked_token = mask_token(coder_session_token)
  print(f"CODER_SESSION_TOKEN: {masked_token}")
  print(f"CODER_API_ROUTE: {coder_api_route}")
  print(f"CODER_ORG_ID: {coder_org_id}")
  print("\n")

def check_environment_variables():
  """
  This function checks if required environment variables are set and warns the user if not.
  """
  required_vars = ["CODER_URL", "CODER_SESSION_TOKEN", "CODER_API_ROUTE", "CODER_ORG_ID"]
  missing_vars = [var for var in required_vars if not os.getenv(var)]
  if missing_vars:
    error_message = "\nERROR: The following environment variables are not set:\n\n"
    for var in missing_vars:
      error_message += f"  - {var}\n"  # Indented with two spaces for each missing variable
    error_message += "\nPlease set these environment variables before running this program.\n"
    print(error_message)
    print_environment_variables()
    sys.exit(1)


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


def format_build_info(build):
  """
  This function formats build information for printing
  """

  release = build.get('version')


  # Split the text at '+'
  parts = release.split('+')

  # Get the first part (everything before '+') and remove leading 'v' if it exists
  release = parts[0]  # add [1:] if you want to remove 'v'
  upgrade_message = build.get('upgrade_message')
  
  dashboard_url = build.get('dashboard_url')
  telemetry = build.get('telemetry')
  deployment_id = build.get('deployment_id')
  workspace_proxy = build.get('workspace_proxy')

  return f"\nDashboard URL: {dashboard_url}\nTelemetry enabled? {telemetry}\nDeployment Id: {deployment_id}\nAdditional Workspace Proxies? {workspace_proxy}\nRelease: {release}"

def check_update():

  api_url = f"{coder_url}/{coder_api_route}/updatecheck"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    process_response(response, "up")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)


def check_api_connection():

  print("\nChecking API connection...\n")
  
  # get release
  api_url = f"{coder_url}/{coder_api_route}/buildinfo"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    #print(response.text)
    process_response(response, "re")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)

# get update available?
  check_update()

  # get user count
  api_url = f"{coder_url}/{coder_api_route}/users"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    process_response(response, "uc")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)  

  # get template count
  api_url = f"{coder_url}/{coder_api_route}/organizations/{coder_org_id}/templates"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    process_response(response, "tc")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)  

  # get workspace count
  api_url = f"{coder_url}/{coder_api_route}/workspaces"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    process_response(response, "wc")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)  

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

      if action.lower() == 'uc':
          user_data = response.json()
          user_count = user_data.get('count')
          print(f"# of users: {user_count}")

      elif action.lower() == 'up':
          update = response.json()
          current = update.get('current')
          version = update.get('version')
          upgrade_message = "Status: "
          url = update.get('url')
          if current:
            upgrade_message = upgrade_message + "on latest version"
          else:
            upgrade_message = upgrade_message + version + " upgrade available at " + url
          print(f"{upgrade_message}")

      elif action.lower() == 're':
          build = response.json()
          release = build.get('version')
          parts = release.split('+')
          release = parts[0] 
          upgrade_message = build.get('upgrade_message')
          print(f"Coder release: {release}")

      elif action.lower() == 'tc':
          template_data = response.json()
          template_count = len(template_data)
          print(f"# of templates: {template_count}")

      elif action.lower() == 'wc':
          workspace_data = response.json()
          workspace_count = workspace_data.get('count')
          print(f"# of workspaces: {workspace_count}")          

      elif action.lower() == 'ui':
          user_data = response.json()
          formatted_user_info = format_user_info(user_data)
          print(formatted_user_info)

      if action.lower() == 'st':
          build_data = response.json()
          formatted_build_info = format_build_info(build_data)
          print(formatted_build_info)
          check_update()


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
        template_data = response.json()
        template_count = len(template_data)
        print(f"\n# of templates: {template_count}\n")

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
          template_version_id = workspace.get('latest_build', {}).get('template_version_id')
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
          if status == 'running': 
            print(f"  Healthy: {health}")

          if outdated:
              print(f"  Deprecated")  # Print 'deprecated' only if 'outdated' is True


          # Construct the API endpoint URL to get resources since the API does not always 
          # return resources in the workspace response i.e., when workspace is stopped
          api_url = f"{coder_url}/{coder_api_route}/templateversions/{template_version_id}/resources"

          # Send the GET request
          response = requests.get(api_url, headers=headers)

          # Process the response
          if response.status_code == 200:
            resources = response.json()
            
            if resources:  

              for resource in resources:
                resource_name = resource.get('name')
                resource_type = resource.get('type')
                workspace_transition = resource.get('workspace_transition')
                dailycost = resource.get('daily_cost')
                if workspace_transition == 'start':
                  print(f"  Type/Resource: {resource_type}/{resource_name}")
                  if dailycost > 0:
                    print(f"  Daily Cost: {dailycost}")                
                  metadata = resource.get('metadata', [])
                  if metadata:
                    print("    Metadata:")
                    for meta in metadata:
                      metadata_key = meta.get('key')
                      metadata_value = meta.get('value')
                      print(f"      - {metadata_key}: {metadata_value}")

                agents = resource.get('agents', [])
                for agent in agents:
                  apps = agent.get('apps', [])
                  if apps:
                      print("    Apps:")
                      for app in apps:
                        display_name = app.get('display_name')
                        if display_name:
                          print(f"      - {display_name}")                  
                      display_apps = agent.get('display_apps')
                      if display_apps:
                        for app in display_apps:
                          print(f"      - {app}")


          else:
              print("Error:", response.status_code)
              print("Error:", response.text)



          print()  # Add a new line after each workspace information


      # Use pretty print to display the JSON data
      #print(json.dumps(data, indent=4))

    except json.JSONDecodeError:
      print("Error: Failed to parse JSON response.")
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)

def main():

    check_environment_variables()
    check_api_connection()

    while True:
        try:

            print("\x1b[5 q")

            print("\n=============================================================")
            print("This is a simple CLI to interact with a Coder CDE deployment!")
            print("=============================================================\n")

            action = input("""Enter:
            'lt' to list templates
            'lw' to list workspaces
            'sw' to search workspaces
            'lu' to list users
            'ui' to list authenticated user info
            'ev' to list environment variables
            'st' to list deployment stats & release
            'q' to exit:
            
            """)

            if action.lower() == 'q':
                print("\n\nExiting...\n\n")
                break

            elif action.lower() == 'sw':
                query = input("\nEnter search query: ")
                api_url = f"{coder_url}/{coder_api_route}/workspaces?q={query}"
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    print(f"\nWorkspaces matching '{query}':\n")
                    process_response(response, 'lw')  # Reuse the existing 'lw' action for processing the response
                else:
                    print("Error:", response.status_code)
                    print("Error:", response.text)

            elif action.lower() == 'ev':
                print_environment_variables()

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
            elif action.lower() == 'st':

                # Construct the API endpoint URL
                api_url = f"{coder_url}/{coder_api_route}/buildinfo"

                # Send the GET request
                response = requests.get(api_url, headers=headers)

                # Process the response
                if response.status_code == 200:
                    print(f"\nDeployment Information:")
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