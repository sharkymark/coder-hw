import os
import sys
import json
import requests

coder_url = os.environ['CODER_URL']
coder_session_token = os.environ['CODER_SESSION_TOKEN']
coder_api_route = os.environ['CODER_API_ROUTE']
coder_org_id = ""
headers = {"Coder-Session-Token": coder_session_token}
verbose = 0

def print_environment_variables():
  print("\nListing environment variables...\n\n")
  print(f"CODER_URL: {coder_url}")
  masked_token = mask_token(coder_session_token)
  print(f"CODER_SESSION_TOKEN: {masked_token}")
  print(f"CODER_API_ROUTE: {coder_api_route}")
  print(f"CODER_ORG_ID: {coder_org_id}")
  print("\n")

  print("\nOverride/correct existing environment variable values? e.g., CODER_URL, CODER_SESSION_TOKEN, CODER_API_ROUTE (y/n) ", end='')
  response = input().lower()

  if response == 'y':
    override_values()

def check_environment_variables():
  """
  This function checks if required environment variables are set and warns the user if not.
  """
  
  required_vars = ["CODER_URL", "CODER_SESSION_TOKEN", "CODER_API_ROUTE"]
  missing_vars = [var for var in required_vars if not os.getenv(var)]
  if missing_vars:
    error_message = "\nERROR: The following environment variables are not set:\n\n"
    for var in missing_vars:
      error_message += f"  - {var}\n"  # Indented with two spaces for each missing variable
    print(error_message)
    
    response = input("Do you want to (1) exit and update your environment variables or (2) manually enter values now? (1/2): ")

    if response == '1':
        print("Exiting program.")
        sys.exit(1)
    elif response == '2':
        override_values()
    else:
        print("Invalid choice. Exiting program.")
        sys.exit(1)

def override_values():
    global coder_url, coder_session_token, coder_api_route, headers

    print(f"\nEnter new value for CODER_URL (press Enter to keep existing value: {coder_url}): ", end='')
    new_coder_url = input()
    if new_coder_url:
        coder_url = new_coder_url

    print(f"Enter new value for CODER_SESSION_TOKEN (press Enter to keep existing value: {coder_session_token}): ", end='')
    new_coder_session_token = input()
    if new_coder_session_token:
        coder_session_token = new_coder_session_token
        headers = {"Coder-Session-Token": coder_session_token}


    print(f"Enter new value for CODER_API_ROUTE (press Enter to keep existing value: {coder_api_route}): ", end='')
    new_coder_api_route = input()
    if new_coder_api_route:
        coder_api_route = new_coder_api_route

    check_api_connection()

def mask_token(token):
    """Masks the middle characters of a token, revealing first 4 and last 4."""
    mask_length = len(token) - 8  # Calculate mask length based on desired reveal
    return f"{token[:4]}{'*' * mask_length}{token[-4:]}"

def get_org_id():
  """
  This function retrieves the organization ID from the Coder API.
  """
  api_url = f"{coder_url}/{coder_api_route}/users/me"

  """
   for debugging
  print(f"API URL: {api_url}")
  print(f"Coder API Route: {coder_api_route}")
  print(f"Coder Session  Token: {coder_session_token}")
  print(f"Headers: {headers}")
  """
  
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    user = response.json()
    org_ids_formatted = format_org_ids(user.get('organization_ids', []))
    first_org_id = user.get('organization_ids', [None])[0]
    print(f"Organization Id in session: {first_org_id}")
    print(f"All Organization Id(s) for user: {org_ids_formatted}")
    return first_org_id
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)
    return None

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

def get_ports(ws_id):

  api_url = f"{coder_url}/{coder_api_route}/workspaces/{ws_id}/port-share"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    
    shares = response.json()
    ports = shares.get('shares', [])
    if ports:
        print("  Shared Ports:")
        for port in ports:
          agent = port.get('agent_name')
          port_num = port.get('port')
          share_level = port.get('share_level')
          print(f"    - {port_num} ({share_level})") 
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)

def extract_ipv4(address_string):
  """
  This function extracts the IP address from a string and returns it.
  """
  # Split the string by :
  parts = address_string.split(":")
  # Get the first part
  ip_address = parts[0]
  return ip_address

import re

def extract_ipv6(address_string):


  match = re.search(r"\[(.*)\]", address_string)
  if match:
    return match.group(1)
  else:
    return None


def count_regions(data):

  regions = data.get("derp", {}).get("regions", {})
  return len(regions)


def count_provisioners(data):
  provisioner_daemons = data.get("provisioner_daemons", {}).get("items", [])
  total_provisioners = 0

  for daemon in provisioner_daemons:
    provisioners = daemon.get("provisioner_daemon", {}).get("provisioners", [])
    total_provisioners += len(provisioners)

  return total_provisioners




def get_health(verbose):

  #print(f"verbose: {verbose}")

  api_url = f"{coder_url}/{coder_api_route}/debug/health"
  response = requests.get(api_url, headers=headers)
  if response.status_code == 200:
    
    health = response.json()
    deployment_health = health.get('healthy')
    derp_health = health.get('derp',{}).get('healthy')
    number_of_regions = count_regions(health)
    udp = health.get('derp',{}).get('netcheck',{}).get('UDP')
    preferred_derp = health.get('derp',{}).get('netcheck',{}).get('PreferredDERP')
    ip4 = extract_ipv4(health.get('derp',{}).get('netcheck',{}).get('GlobalV4'))
    ip6 = extract_ipv6(health.get('derp',{}).get('netcheck',{}).get('GlobalV6'))
    access_url = health.get('access_url',{}).get('access_url')
    access_url_healthy = health.get('access_url',{}).get('healthy')
    access_url_reachable = health.get('access_url',{}).get('reachable')
    access_url_status_code = health.get('access_url',{}).get('status_code')
    websocket_healthy = health.get('websocket',{}).get('healthy')
    db_healthy = health.get('database',{}).get('healthy')
    db_latency = health.get('database',{}).get('latency')
    wsp_healthy = health.get('workspace_proxy',{}).get('healthy')
    total_provisioners = count_provisioners(health)
  

    if verbose == 0:
      print(f"Deployment healthy: {deployment_health}")
  

    if verbose != 0:
      while True:
        try:
          verbose = int(input("\nEnter health verbosity level (1 for key deployment data points, 2 for full output): "))
          if verbose in [1, 2]:
            break
          else:
            print("Incorrect value. Please enter 1 or 2.")
        except ValueError:
          print("Invalid input. Please enter a number.")

      if verbose == 1:
        print(f"\nDeployment healthy: {deployment_health}")
        print(f"Database:")
        print(f"  Healthy: {db_healthy}")
        print(f"  Latency: {db_latency}")
        print(f"Networking:")
        print(f"  Designated Encrypted Relay for Packets \"DERP\" servers healthy: {derp_health}")
        print(f"  # of DERP regions: {number_of_regions}")
        print(f"  UDP healthy: {udp}")
        print(f"  Websocket healthy: {websocket_healthy}")
        print(f"  Preferred DERP server: {preferred_derp}")
        print(f"  IP4: {ip4}")
        print(f"  IP6: {ip6}")
        print(f"Access URL: {access_url}")
        print(f"  Healthy: {access_url_healthy}")
        print(f"  Reachable: {access_url_reachable}")
        print(f"  Status code: {access_url_status_code}")
        print(f"Workspace proxy healthy: {wsp_healthy}")
        print(f"# of provisioners: {total_provisioners}")
      elif verbose == 2:
        print("\n\n")
        print(json.dumps(health, indent=4))
      
  else:
    print("Error:", response.status_code)
    print("Error:", response.text)

def check_api_connection():

  global coder_org_id

  print("\nChecking API connection...\n")
  
  # print org ids and set coder_org_id
  coder_org_id = get_org_id()


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
  # get health status
  get_health(0)

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

def update_workspace_state(transition, chosen_workspace):
  """
  This function sends a POST request to the Coder API to start or stop a workspace.

  Args:
      transition (str): The desired transition state ("start" or "stop").

  Returns:
      bool: True if the API call was successful, False otherwise.
  """  

  api_url = f"{coder_url}/{coder_api_route}/workspaces/{chosen_workspace['id']}/builds"
  headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      "Coder-Session-Token": coder_session_token
  }
  data = json.dumps({'transition': transition})

  try:
      response = requests.post(api_url, headers=headers, data=data)
      response.raise_for_status()  # Raise an exception for non-200 status codes
      return True
  except requests.exceptions.RequestException as e:
      print(f"Error updating workspace state: {e}")
      return False


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
          upgrade_message = "Release status: "
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
        for i, workspace in enumerate(response.json()['workspaces']):
          name = workspace.get('name')
          ws_id = workspace.get('latest_build', {}).get('workspace_id')
          template_name = workspace.get('template_name')
          template_version = workspace.get('latest_build', {}).get('template_version_name')
          template_version_id = workspace.get('latest_build', {}).get('template_version_id')
          health = workspace.get('health', {}).get('healthy')
          status = workspace.get('latest_build', {}).get('status')
          outdated = workspace.get('outdated', False)
          last_built = workspace.get('latest_build', {}).get('created_at')
          owner = workspace.get('latest_build', {}).get('workspace_owner_name')
          

          print(f"  Workspace #{i+1}")
          print(f"  Name (Id): {name} ({ws_id})")
          print(f"  Owner: {owner}")
          print(f"  Template (version | id): {template_name} ({template_version} | {template_version_id})")
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

            get_ports(ws_id)

            print()  # Add a new line after each workspace information

          else:
              print("Error:", response.status_code)
              print("Error:", response.text)



        #print("\n\nSelect a workspace by number (or 'q' to quit):")
        #user_choice = input("> ")

        user_choice = input("\n\nSelect a workspace by number (or 'q' to quit): ")

        if not workspaces:
            print("\nNo workspaces found.")
            return  # Exit the function if no workspaces

        while True:

          if user_choice.lower() == 'q':
              return  # Exit the function if user chooses 'q'

          try:
              workspace_index = int(user_choice) - 1  # Convert to zero-based index
              if workspace_index >= 0 and workspace_index < len(workspaces):
                  # Valid selection, proceed with chosen workspace
                  chosen_workspace = workspaces[workspace_index]
                  print(f"\nWorkspace selected:")
                  print(f"  Name: {chosen_workspace['name']}")
                  print(f"  Owner: {chosen_workspace['owner_name']}")
                  print(f"  Template: {chosen_workspace['template_name']} ({chosen_workspace['latest_build']['template_version_name']})")
                  print(f"  Status: {chosen_workspace.get('latest_build', {}).get('status')}")
                  print(f"  List Number: {user_choice}")
                  break  # Exit the loop on valid selection
              else:
                  print(f"\nInvalid choice. Please enter a positive number between 1 and {len(workspaces)}. Returning to main menu.")
                  return
              
          except ValueError:
              print("\nInvalid input. Please enter a number or 'q'.")
              return


        valid_choices = {"1": "start", "2": "stop"}  # Map number to action
        transition_input = input("\nEnter 1 to start the workspace, 2 to stop it (or 'q' to quit): ")

        if transition_input in valid_choices:
          transition = valid_choices[transition_input]
          success = update_workspace_state(transition,chosen_workspace)
          if success:
            print(f"\nWorkspace successfully {'started' if transition == 'start' else 'stopped'}.")
            print(f"  Name: {chosen_workspace['name']}")
            print(f"  List Number: {user_choice}")
          else:
            print("\nError updating workspace state. Please try again.")
        else:
          print("\nInvalid choice. Please enter 1, 2, or 'q'. Returning to main menu.")


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
            'lw' to list, start, stop workspaces
            'sw' to search workspaces
            'lu' to list users
            'ui' to list authenticated user info
            'ev' to list or inline change environment variables
            'hc' to do a health check and show details
            'st' to list deployment stats & release
            'q' to exit:
            
            """)

            if action.lower() == 'q':
                print("\n\nExiting...\n\n")
                break
            elif action.lower() == 'hc':
                get_health(1)
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